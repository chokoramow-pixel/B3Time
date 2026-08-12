from django.urls import path

from eventos import views

app_name = "eventos"

urlpatterns = [
    path("", views.lista_eventos, name="lista"),
    path("panel/", views.panel_eventos, name="panel_lista"),
    path("panel/exportar/", views.exportar_eventos, name="panel_exportar"),
    path("panel/crear/", views.crear_evento, name="crear"),
    path("panel/<int:evento_id>/editar/", views.editar_evento, name="editar"),
    path("panel/<int:evento_id>/eliminar/", views.eliminar_evento, name="eliminar"),
    path("<int:evento_id>/", views.detalle_evento, name="detalle"),
]
