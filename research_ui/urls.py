from django.urls import path
from . import views
from test_series import routes as ts_routes

app_name = "research_ui"

urlpatterns = [
    path("", views.index, name="index"),
    path("test-series/", views.test_series_view, name="test_series"),
    
    # Admin Portal Views & Auth
    path("test-series/admin/login/", ts_routes.admin_login_view, name="ts_admin_login"),
    path("test-series/admin/logout/", ts_routes.admin_logout_view, name="ts_admin_logout"),
    path("test-series/admin/", ts_routes.admin_dashboard_view, name="ts_admin_dashboard"),

    # UPSC & Multi-Exam Test Series & RAG API endpoints
    path("api/test-series/exams/", ts_routes.get_exams_api, name="ts_exams"),
    path("api/test-series/config/", ts_routes.get_config_api, name="ts_config"),
    path("api/test-series/admin/config/update/", ts_routes.update_config_api, name="ts_admin_config_update"),
    path("api/test-series/admin/upload-pdf/", ts_routes.upload_pdf_api, name="ts_admin_upload_pdf"),
    path("api/test-series/admin/clear-subject/", ts_routes.clear_subject_api, name="ts_admin_clear_subject"),
    path("api/test-series/admin/sessions/", ts_routes.get_admin_sessions_api, name="ts_admin_sessions"),

    path("api/test-series/upsc/subjects/", ts_routes.get_subjects_api, name="ts_upsc_subjects"),
    path("api/test-series/upsc/<str:subject>/", ts_routes.get_subject_detail_api, name="ts_upsc_subject_detail"),
    path("api/test-series/upsc/<str:subject>/start/", ts_routes.start_test_api, name="ts_upsc_start"),
    path("api/test-series/session/<str:session_id>/question/<int:q_index>/", ts_routes.get_question_api, name="ts_get_question"),
    path("api/test-series/session/<str:session_id>/next-question/", ts_routes.next_question_api, name="ts_next_question"),
    path("api/test-series/session/<str:session_id>/answer/", ts_routes.record_answer_api, name="ts_record_answer"),
    path("api/test-series/session/<str:session_id>/submit/", ts_routes.submit_test_api, name="ts_submit_test"),
    path("api/test-series/session/<str:session_id>/results/", ts_routes.get_results_api, name="ts_get_results"),
    path("api/test-series/session/<str:session_id>/review/", ts_routes.get_results_api, name="ts_get_review"),
    path("api/test-series/ingest/status/", ts_routes.get_ingest_status_api, name="ts_ingest_status"),
    path("api/test-series/ingest/run/", ts_routes.trigger_ingest_api, name="ts_ingest_run"),

    path("api/chat/", views.chat_api, name="chat_api"),
    path("api/reports/", views.reports_api, name="reports_api"),
    path(
        "api/reports/download/<path:relpath>",
        views.download_report,
        name="download_report",
    ),
    path(
        "api/reports/preview/<path:relpath>",
        views.preview_report,
        name="preview_report",
    ),
    path("api/status/", views.status_api, name="status_api"),
    path("api/reset/", views.reset_api, name="reset_api"),
    path("api/conversations/", views.conversations_list_api, name="conversations_list"),
    path("api/conversations/clear/", views.conversations_clear_api, name="conversations_clear"),
    path("api/conversations/<str:conv_id>/", views.conversation_detail_api, name="conversation_detail"),
    path("api/conversations/<str:conv_id>/delete/", views.conversation_delete_api, name="conversation_delete"),
    path("api/conversations/<str:conv_id>/message/edit/", views.conversation_edit_message_api, name="conversation_edit_message"),
    path("api/upload/", views.upload_file_api, name="upload_file"),
    path("api/uploads/", views.uploads_list_api, name="uploads_list"),
    path("api/uploads/download/<path:relpath>", views.download_upload_file, name="download_upload_file"),
    path("api/uploads/preview/<path:relpath>", views.preview_upload_file, name="preview_upload_file"),
    path("favicon.ico", views.favicon_view, name="favicon"),
]
