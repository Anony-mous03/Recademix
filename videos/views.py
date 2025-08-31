from django.shortcuts import render, redirect, get_object_or_404
from .models import Course, Topic, UserCourse, Field, VideoProgress
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.db.models import Prefetch
import requests
import json
import re

from django.conf import settings
YOUTUBE_API_KEY = getattr(settings, 'YOUTUBE_API_KEY', '')

def parse_duration(duration):
    """Parse YouTube API duration format (PT4M13S) to readable format (4:13)"""
    if not duration:
        return ''
    
    match = re.match(r'PT(?:(\d+)H)?(?:(\d+)M)?(?:(\d+)S)?', duration)
    if not match:
        return ''
    
    hours, minutes, seconds = match.groups()
    hours = int(hours or 0)
    minutes = int(minutes or 0)
    seconds = int(seconds or 0)
    
    if hours > 0:
        return f"{hours}:{minutes:02d}:{seconds:02d}"
    else:
        return f"{minutes}:{seconds:02d}"

def get_video_details(video_ids):
    """Get additional video details like duration and view count"""
    if not video_ids:
        return {}
    
    url = 'https://www.googleapis.com/youtube/v3/videos'
    params = {
        'part': 'contentDetails,statistics',
        'id': ','.join(video_ids),
        'key': YOUTUBE_API_KEY
    }
    
    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        
        data = response.json()
        details = {}
        
        for item in data.get('items', []):
            video_id = item['id']
            content_details = item.get('contentDetails', {})
            statistics = item.get('statistics', {})
            
            details[video_id] = {
                'duration': parse_duration(content_details.get('duration', '')),
                'viewCount': int(statistics.get('viewCount', 0))
            }
        
        return details
        
    except Exception as e:
        print(f"Error fetching video details: {e}")
        return {}

def fetch_youtube_topics(query, max_results=10):
    """Enhanced YouTube API function to fetch videos with thumbnails and metadata"""
    url = 'https://www.googleapis.com/youtube/v3/search'
    params = {
        'part': 'snippet',
        'q': f"{query} tutorial programming course",
        'type': 'video',
        'maxResults': max_results,
        'key': YOUTUBE_API_KEY,
        'order': 'relevance',
        'videoDuration': 'medium',
        'videoDefinition': 'high',
        'relevanceLanguage': 'en'
    }
    
    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        
        data = response.json()
        items = data.get('items', [])
        
        # Get additional video details
        video_ids = [item['id']['videoId'] for item in items]
        video_details = get_video_details(video_ids)
        
        videos = []
        for item in items:
            video_id = item['id']['videoId']
            snippet = item['snippet']
            details = video_details.get(video_id, {})
            
            videos.append({
                'name': snippet['title'],
                'url': f"https://www.youtube.com/embed/{video_id}",
                'thumbnail': snippet['thumbnails'].get('medium', {}).get('url', ''),
                'channel': snippet['channelTitle'],
                'published': snippet['publishedAt'],
                'description': snippet.get('description', '')[:200],
                'duration': details.get('duration', ''),
                'view_count': details.get('viewCount', 0)
            })
        
        return videos
        
    except requests.RequestException as e:
        print(f"Error fetching YouTube videos: {e}")
        return []
    except Exception as e:
        print(f"Unexpected error: {e}")
        return []

def create_topics_for_course(course, max_results=15):
    """Helper function to create topics for a course"""
    if course.topics.exists():
        return 0  # Topics already exist
    
    results = fetch_youtube_topics(course.title, max_results=max_results)
    topics_created = 0
    
    for res in results:
        try:
            Topic.objects.create(
                course=course,
                name=res["name"],
                url=res["url"],
                description=res.get("description", ""),
                is_recommended=True
            )
            topics_created += 1
        except Exception as e:
            print(f"Error creating topic: {e}")
    
    return topics_created

def get_grouped_courses():
    """Helper function to get courses grouped by field"""
    try:
        # Method 1: Get all fields that have courses
        fields_with_courses = Field.objects.prefetch_related('courses').filter(courses__isnull=False).distinct()
        grouped_courses = []
        
        for field in fields_with_courses:
            courses = field.courses.all()
            if courses.exists():
                grouped_courses.append((field.name, courses))
        
        # If no grouped courses, try alternative method
        if not grouped_courses:
            all_courses = Course.objects.select_related('field').all()
            field_course_dict = {}
            
            for course in all_courses:
                field_name = course.field.name if course.field else "Uncategorized"
                if field_name not in field_course_dict:
                    field_course_dict[field_name] = []
                field_course_dict[field_name].append(course)
            
            grouped_courses = list(field_course_dict.items())
        
        return grouped_courses
        
    except Exception as e:
        print(f"Error getting grouped courses: {e}")
        return []

@login_required
def course_registration(request):
    """Course registration view with sidebar interface"""
    if request.method == "POST":
        selected_ids = request.POST.getlist("course")
                        
        if not selected_ids:
            messages.error(request, "Please select at least one course.")
        else:
            enrolled_count = 0
            already_enrolled = []
            
            for course_id in selected_ids:
                try:
                    course = Course.objects.get(id=course_id)
                    user_course, created = UserCourse.objects.get_or_create(
                        user=request.user,
                        course=course
                    )
                                        
                    if created:
                        enrolled_count += 1
                        # Auto-generate topics
                        topics_created = create_topics_for_course(course)
                        if topics_created > 0:
                            messages.success(request, f"Enrolled in {course.title} with {topics_created} videos!")
                        else:
                            messages.warning(request, f"Enrolled in {course.title} but no videos found.")
                    else:
                        already_enrolled.append(course.title)
                                    
                except Course.DoesNotExist:
                    messages.error(request, f"Course with ID {course_id} does not exist.")
                except Exception as e:
                    messages.error(request, f"Error processing course {course_id}: {str(e)}")
                        
            # Summary messages
            if enrolled_count > 0 and enrolled_count < 2:
                messages.success(request, "Your course have been successfully enrolled!")
                return redirect("dashboard")
            
            if enrolled_count > 1 :
                messages.success(request, f"You have succesfully enrolled your courses!")
                return redirect("dashboard")
                
            if already_enrolled: 
                messages.info(request, f"Already enrolled in: {', '.join(already_enrolled)}")
                return redirect("course_registration")
                                

    # Get fields with courses for display
    fields = Field.objects.prefetch_related('courses').order_by('name')
    
    # Add course count to each field
    for field in fields:
        field.course_count = field.courses.count()
    
    context = {
        'fields': fields
    }
    return render(request, 'course-registration.html', context)

@login_required
def my_courses(request):
    """Display user's enrolled courses (simplified version)"""
    # Get all courses the user is enrolled in
    user_courses = UserCourse.objects.filter(user=request.user).select_related('course')
    
    if not user_courses.exists():
        return render(request, 'courses.html', {'no_courses': True})
    
    # Prepare course data with topic counts
    courses_data = []
    total_topics = 0
    completed_topics = 0
    
    for user_course in user_courses:
        course = user_course.course
        
        # Count topics for this course
        topic_count = Topic.objects.filter(course=course).count()
        total_topics += topic_count
        
        # Count completed topics for this course
        course_topics = Topic.objects.filter(course=course)
        for topic in course_topics:
            if VideoProgress.objects.filter(user=request.user, topic=topic, completed=True).exists():
                completed_topics += 1
        
        # Add topic count to course object
        course.topic_count = topic_count
        courses_data.append(course)
    
    # Calculate progress percentage
    progress_percentage = 0
    if total_topics > 0:
        progress_percentage = round((completed_topics / total_topics) * 100)
    
    context = {
        'user_courses': courses_data,
        'total_courses': len(courses_data),
        'total_topics': total_topics,
        'progress_percentage': progress_percentage,
        'no_courses': False,
    }
    
    return render(request, 'courses.html', context)

@login_required
def edit_courses(request):
    """Edit user's course enrollments with sidebar interface"""
    if request.method == 'POST':
        selected_courses = request.POST.getlist('courses')
        selected_courses = set(map(int, selected_courses)) if selected_courses else set()
        user = request.user
        
        # Get current enrolled courses
        current_courses = set(UserCourse.objects.filter(user=user).values_list('course_id', flat=True))
        
        # Add new courses
        courses_to_add = selected_courses - current_courses
        for course_id in courses_to_add:
            try:
                course = Course.objects.get(id=course_id)
                UserCourse.objects.create(user=user, course=course)
                
                # Generate topics if needed
                topics_created = create_topics_for_course(course)
                if topics_created > 0:
                    messages.success(request, f"Added {course.title} with {topics_created} videos!")
                else:
                    messages.success(request, f"Added {course.title}")
                    
            except Course.DoesNotExist:
                messages.error(request, f"Course with ID {course_id} not found.")
        
        # Remove unchecked courses
        courses_to_remove = current_courses - selected_courses
        if courses_to_remove:
            removed_courses = Course.objects.filter(id__in=courses_to_remove)
            course_names = [course.title for course in removed_courses]
            UserCourse.objects.filter(user=user, course_id__in=courses_to_remove).delete()
            messages.success(request, f"Removed courses: {', '.join(course_names)}")
        
        return redirect('my_courses')
    
    else:
        # Get currently enrolled courses
        enrolled_course_ids = set(
            UserCourse.objects.filter(user=request.user).values_list('course_id', flat=True)
        )
        
        # Get fields with courses and enrollment status
        fields = Field.objects.prefetch_related('courses').order_by('name')
        
        # Add course count and enrollment status to each field/course
        for field in fields:
            field.course_count = field.courses.count()
            for course in field.courses.all():
                course.is_enrolled = course.id in enrolled_course_ids
        
        context = {
            'fields': fields,
            'enrolled_course_ids': enrolled_course_ids,
        }
        
        return render(request, 'edit-courses.html', context)

@login_required
def dashboard(request):
    user = request.user
    
    # Get user's courses
    user_courses = UserCourse.objects.filter(user=user).select_related('course')
    course_count = user_courses.count()
    
    # Get recently watched videos
    recent_videos = VideoProgress.objects.filter(user=user).order_by('-watched_date')[:5]
    
    # Get recommended videos (not watched yet)
    watched_topics = VideoProgress.objects.filter(user=user).values_list('topic_id', flat=True)
    user_course_ids = user_courses.values_list('course_id', flat=True)
    recommended_videos = Topic.objects.filter(
        course_id__in=user_course_ids,
        is_recommended=True
    ).exclude(id__in=watched_topics)[:5]
    
    # Get stats
    videos_watched = VideoProgress.objects.filter(user=user).count()
    videos_completed = VideoProgress.objects.filter(user=user, completed=True).count()
    
    # Calculate completion percentage
    if videos_watched > 0:
        completion_percentage = (videos_completed / videos_watched) * 100
    else:
        completion_percentage = 0
    
    context = {
        'course_count': course_count,
        'recent_videos': recent_videos,
        'recommended_videos': recommended_videos,
        'videos_watched': videos_watched,
        'videos_completed': videos_completed,
        'completion_percentage': completion_percentage,
        'user_courses': user_courses,
    }
    
    return render(request, 'dashboard.html', context)

@login_required
def refresh_course_videos(request, course_id):
    """AJAX view to refresh videos for a specific course"""
    if request.method == 'POST':
        try:
            course = get_object_or_404(Course, id=course_id)
            
            # Check if user is enrolled
            if not UserCourse.objects.filter(user=request.user, course=course).exists():
                return JsonResponse({'success': False, 'error': 'Not enrolled in this course'})
            
            # Delete existing topics and fetch new ones
            course.topics.all().delete()
            topics_created = create_topics_for_course(course)
            
            return JsonResponse({
                'success': True, 
                'message': f'Refreshed {topics_created} videos for {course.title}',
                'video_count': topics_created
            })
            
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    
    return JsonResponse({'success': False, 'error': 'Invalid request method'})

@login_required
def track_video_progress(request):
    """Track user's video watching progress"""
    if request.method == 'POST':
        data = json.loads(request.body)
        topic_id = data.get('topic_id')
        duration = data.get('duration', 0)
        completed = data.get('completed', False)
        
        try:
            topic = Topic.objects.get(id=topic_id)
            progress, created = VideoProgress.objects.get_or_create(
                user=request.user,
                topic=topic,
                defaults={'watch_duration': duration, 'completed': completed}
            )
            
            if not created:
                progress.watch_duration = duration
                progress.completed = completed
                progress.save()
                
            return JsonResponse({'status': 'success'})
        except Topic.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'Topic not found'}, status=404)
    
    return JsonResponse({'status': 'error', 'message': 'Invalid request'}, status=400)

@login_required
def course_topics(request, course_id):
    """Display all topics for a specific course"""
    try:
        # Get the course and verify user is enrolled
        course = Course.objects.get(id=course_id)
        user_course = UserCourse.objects.get(user=request.user, course=course)
        
    except (Course.DoesNotExist, UserCourse.DoesNotExist):
        # Redirect to courses page if course doesn't exist or user not enrolled
        messages.error(request, "Course not found or you're not enrolled in this course.")
        return redirect('my_courses')
    
    # Get all topics for this course with user progress
    topics = Topic.objects.filter(course=course).prefetch_related(
        Prefetch(
            'videoprogress_set',
            queryset=VideoProgress.objects.filter(user=request.user),
            to_attr='user_progress'
        )
    ).order_by('uploaded')
    
    # Add progress information to each topic
    completed_count = 0
    for topic in topics:
        topic.progress = None
        if hasattr(topic, 'user_progress') and topic.user_progress:
            topic.progress = topic.user_progress[0]
            if topic.progress.completed:
                completed_count += 1
    
    context = {
        'course': course,
        'topics': topics,
        'completed_count': completed_count,
    }
    
    return render(request, 'topics.html', context)