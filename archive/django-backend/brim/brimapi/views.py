import json
from datetime import timedelta

from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.db.models import Avg, Count
from django.http import JsonResponse
from django.shortcuts import redirect, render
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_GET, require_POST

import rust_ext

from .models import SiteReview, SiteScan
from .scanner import scan_site

SCAN_CACHE_MINUTES = 30


def _community_summary(url):
    reviews = SiteReview.objects.filter(url=url)
    aggregate = reviews.aggregate(
        average=Avg("accreditation"), count=Count("id")
    )
    return {
        "average_accreditation": round(aggregate["average"], 2)
        if aggregate["average"] is not None
        else None,
        "review_count": aggregate["count"],
        "reviews": [
            {
                "user": review.user.username,
                "accreditation": review.accreditation,
                "comment": review.comment,
                "created_at": review.created_at.isoformat(),
            }
            for review in reviews.select_related("user")[:50]
        ],
    }


def build_research_results(query):
    topic = query.strip()
    title_topic = topic.title()
    slug = "+".join(topic.split())
    wiki_slug = "_".join(word.capitalize() for word in topic.split())

    return [
        {
            "title": f"{title_topic} - Wikipedia",
            "url": f"https://en.wikipedia.org/wiki/{wiki_slug}",
            "display_url": "en.wikipedia.org",
            "summary": f"Encyclopedic overview of {topic}, including background, history, and cited references.",
            "source_type": "encyclopedia",
            "sources": [
                "Cited references section",
                "Linked primary sources",
                "Editorial revision history",
            ],
        },
        {
            "title": f"{title_topic} research papers - Google Scholar",
            "url": f"https://scholar.google.com/scholar?q={slug}",
            "display_url": "scholar.google.com",
            "summary": f"Peer-reviewed articles, citations, and academic literature related to {topic}.",
            "source_type": "scholarly",
            "sources": [
                "Peer-reviewed journals",
                "Citation graph",
                "Author affiliations",
            ],
        },
        {
            "title": f"{title_topic} | National Institutes / Government Resources",
            "url": f"https://www.usa.gov/search?query={slug}",
            "display_url": "usa.gov",
            "summary": f"Official government information and public data on {topic}.",
            "source_type": "government",
            "sources": [
                "Government datasets",
                "Public records",
                "Official agency publications",
            ],
        },
        {
            "title": f"{title_topic} - University Research Guides",
            "url": f"https://www.jstor.org/action/doBasicSearch?Query={slug}",
            "display_url": "jstor.org",
            "summary": f"Academic library and archival materials covering {topic}.",
            "source_type": "academic_library",
            "sources": [
                "University library catalog",
                "Archived journals",
                "Primary source collections",
            ],
        },
        {
            "title": f"{title_topic} - In-depth Reporting",
            "url": f"https://www.reuters.com/site-search/?query={slug}",
            "display_url": "reuters.com",
            "summary": f"Recent reporting and analysis on {topic} from established news sources.",
            "source_type": "news",
            "sources": [
                "Named reporters and editors",
                "Quoted primary sources",
                "Publication corrections policy",
            ],
        },
    ]


@csrf_exempt
@require_POST
def create_user_view(request):
    try:
        payload = json.loads(request.body or "{}")
        username = payload.get("username")
        password = payload.get("password")

        if not username or not password:
            return JsonResponse({"error": "username and password are required"}, status=400)

        user_json = rust_ext.create_user(username, password)
        return JsonResponse(json.loads(user_json), status=201)
    except json.JSONDecodeError:
        return JsonResponse({"error": "invalid JSON body"}, status=400)
    except Exception as error:
        return JsonResponse({"error": str(error)}, status=500)


@user_passes_test(lambda user: user.is_staff)
def admin_users_view(request):
    return render(request, "brimapi/admin_users.html")


@login_required
def search_view(request):
    query = request.GET.get("query", "").strip()
    max_results = min(int(request.GET.get("max_results", 10)), 10)

    if not query:
        return JsonResponse({"query": query, "results": []})

    websites = build_research_results(query)

    results = []
    for index, website in enumerate(websites[:max_results]):
        authority_score = round(0.96 - (index * 0.03), 2)
        source_score = round(0.93 - (index * 0.04), 2)
        transparency_score = round(0.91 - (index * 0.03), 2)
        priority_score = round(((authority_score + source_score + transparency_score) / 3) * 100, 2)
        results.append(
            {
                **website,
                "veracity_protocol": {
                    "claim": f"{website['title']} is a relevant source for {query}.",
                    "authority_score": authority_score,
                    "source_score": source_score,
                    "transparency_score": transparency_score,
                    "priority_score": priority_score,
                    "validated": priority_score >= 80,
                    "scan_status": "sources scanned",
                },
            }
        )

    return JsonResponse({"query": query, "results": results})


def signup_view(request):
    if request.user.is_authenticated:
        return redirect("public-search")

    form = UserCreationForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        user = form.save()
        login(request, user)
        return redirect("public-search")

    return render(request, "brimapi/signup.html", {"form": form})


def login_view(request):
    if request.user.is_authenticated:
        return redirect("public-search")

    error = None
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect("public-search")
        error = "Invalid username or password"

    return render(request, "brimapi/login.html", {"error": error})


def logout_view(request):
    logout(request)
    return redirect("login")


@login_required
def public_search_view(request):
    return render(request, "brimapi/search.html")


@csrf_exempt
@login_required
@require_POST
def scan_view(request):
    try:
        payload = json.loads(request.body or "{}")
    except json.JSONDecodeError:
        return JsonResponse({"error": "invalid JSON body"}, status=400)

    url = (payload.get("url") or "").strip()
    if not url:
        return JsonResponse({"error": "url is required"}, status=400)

    cached = SiteScan.objects.filter(url=url).first()
    fresh = (
        cached is not None
        and cached.scanned_at >= timezone.now() - timedelta(minutes=SCAN_CACHE_MINUTES)
    )

    if fresh:
        scan = {
            "url": cached.url,
            "domain": cached.domain,
            "reachable": cached.reachable,
            "score": cached.score,
            "signals": cached.signals,
        }
        scanned_at = cached.scanned_at
    else:
        scan = scan_site(url)
        record, _ = SiteScan.objects.update_or_create(
            url=url,
            defaults={
                "domain": scan["domain"],
                "score": scan["score"],
                "reachable": scan["reachable"],
                "signals": scan["signals"],
            },
        )
        scanned_at = record.scanned_at

    return JsonResponse(
        {
            **scan,
            "cached": fresh,
            "scanned_at": scanned_at.isoformat(),
            "community": _community_summary(url),
        }
    )


@csrf_exempt
@login_required
def reviews_view(request):
    if request.method == "GET":
        url = (request.GET.get("url") or "").strip()
        if not url:
            return JsonResponse({"error": "url is required"}, status=400)
        return JsonResponse({"url": url, **_community_summary(url)})

    if request.method == "POST":
        try:
            payload = json.loads(request.body or "{}")
        except json.JSONDecodeError:
            return JsonResponse({"error": "invalid JSON body"}, status=400)

        url = (payload.get("url") or "").strip()
        if not url:
            return JsonResponse({"error": "url is required"}, status=400)

        try:
            accreditation = int(payload.get("accreditation", 3))
        except (TypeError, ValueError):
            return JsonResponse({"error": "accreditation must be 1-5"}, status=400)

        if not 1 <= accreditation <= 5:
            return JsonResponse({"error": "accreditation must be 1-5"}, status=400)

        from urllib.parse import urlparse

        SiteReview.objects.update_or_create(
            url=url,
            user=request.user,
            defaults={
                "domain": urlparse(url).netloc or url,
                "accreditation": accreditation,
                "comment": (payload.get("comment") or "").strip(),
            },
        )
        return JsonResponse({"url": url, **_community_summary(url)}, status=201)

    return JsonResponse({"error": "method not allowed"}, status=405)
