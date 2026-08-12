from django.urls import path

from publicaciones import views

app_name = "publicaciones"

urlpatterns = [
    path("", views.lista_publicaciones, name="lista"),
    path("panel/", views.panel_publicaciones, name="panel_lista"),
    path("panel/exportar/", views.exportar_publicaciones, name="panel_exportar"),
    path("panel/crear/", views.crear_publicacion, name="crear"),
    path("panel/<int:publicacion_id>/editar/", views.editar_publicacion, name="editar"),
    path("panel/<int:publicacion_id>/eliminar/", views.eliminar_publicacion, name="eliminar"),
    path("<int:publicacion_id>/", views.detalle_publicacion, name="detalle"),
]
