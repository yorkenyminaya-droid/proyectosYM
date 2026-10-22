<?php

$mes = $_POST['mes'];
$fecha = $_POST['fecha'];
$actividad = preg_replace('/[^A-Za-z0-9_-]/', '_', $_POST['actividad']);

$ruta = "Fotos/$mes/$fecha/$actividad/";

if (!file_exists($ruta)) {
    mkdir($ruta, 0777, true);
}

$total = count($_FILES['fotos']['name']);

for ($i = 0; $i < $total; $i++) {

    $nombre = basename($_FILES['fotos']['name'][$i]);

    move_uploaded_file(
        $_FILES['fotos']['tmp_name'][$i],
        $ruta . $nombre
    );
}

echo "<h2>Fotografías cargadas correctamente.</h2>";
echo "<a href='index.php'>Volver</a>";

?>
