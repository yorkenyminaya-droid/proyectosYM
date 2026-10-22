<?php
$mes = $_GET['mes'] ?? '';
?>

<!DOCTYPE html>

<html>
<head>
<meta charset="UTF-8">
<title>Galería</title>
<link rel="stylesheet" href="estilos.css">
</head>
<body>

<h1>Galería Institucional</h1>

<form method="GET">

<select name="mes">
<option value="">Seleccione Mes</option>

<?php
$meses = glob("Fotos/*", GLOB_ONLYDIR);

foreach($meses as $m){
    $nombre = basename($m);

    $selected = ($mes == $nombre) ? "selected" : "";

    echo "<option $selected>$nombre</option>";
}
?>

</select>

<button>Mostrar</button>

</form>

<div class="galeria">

<?php

if($mes != ""){

    $imagenes = glob("Fotos/$mes/*/*/*.{jpg,jpeg,png,JPG,PNG}", GLOB_BRACE);

    foreach($imagenes as $img){

        echo "
        <div class='foto'>
            <a href='$img' target='_blank'>
                <img src='$img'>
            </a>

            <br>

            <a download href='$img'>Descargar</a>
        </div>";
    }
}

?>

</div>

</body>
</html>
