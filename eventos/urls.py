from django.urls import path

from eventos import views

app_name = "eventos"

urlpatterns = [
    path("", views.lista_eventos, name="lista"),
    path("panel/", views.EventoListView.as_view(), name="panel_lista"),
    path("panel/exportar/", views.exportar_eventos, name="panel_exportar"),
    path("panel/crear/", views.EventoCreateView.as_view(), name="crear"),
    path("panel/<int:pk>/editar/", views.EventoUpdateView.as_view(), name="editar"),
    path("panel/<int:pk>/eliminar/", views.EventoDeleteView.as_view(), name="eliminar"),
    path("panel/<int:evento_id>/inscritos/", views.checklist_inscritos, name="panel_inscritos"),
    path("<int:evento_id>/", views.detalle_evento, name="detalle"),
    path("<int:evento_id>/inscribirse/", views.inscribirse_evento, name="inscribirse"),
]
