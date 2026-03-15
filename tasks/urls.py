from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import TaskViewSet, TaskCommentViewSet, TaskStatusLogViewSet

router = DefaultRouter()
router.register(r'comments', TaskCommentViewSet, basename='taskcomment')
router.register(r'logs', TaskStatusLogViewSet, basename='taskstatuslog')
router.register(r'', TaskViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('<int:pk>/change_status/', TaskViewSet.as_view({'post': 'change_status'}), name='task-change-status'),
    path('<int:pk>/add_comment/', TaskViewSet.as_view({'post': 'add_comment'}), name='task-add-comment'),
]
