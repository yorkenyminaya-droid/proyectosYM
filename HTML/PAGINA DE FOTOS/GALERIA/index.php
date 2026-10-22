<!DOCTYPE html>

<html>
<head>
    <meta charset="UTF-8">
    <title>Galería Institucional</title>
    <link rel="stylesheet" href="estilos.css">
</head>
<body>

<h1>Subir Fotografías</h1>

<form action="subir.php" method="POST" enctype="multipart/form-data">

```
<label>Mes:</label>
<select name="mes">
    <option>Enero</option>
    <option>Febrero</option>
    <option>Marzo</option>
    <option>Abril</option>
    <option>Mayo</option>
    <option>Junio</option>
    <option>Julio</option>
    <option>Agosto</option>
    <option>Septiembre</option>
    <option>Octubre</option>
    <option>Noviembre</option>
    <option>Diciembre</option>
</select>

<label>Fecha:</label>
<input type="date" name="fecha" required>

<label>Actividad:</label>
<input type="text" name="actividad" required>

<label>Fotografías:</label>
<input type="file" name="fotos[]" multiple required>

<button type="submit">Subir Fotos</button>
```

</form>

<hr>

<a href="galeria.php">Ver Galería</a>

</body>
</html>
