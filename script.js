async function cargarImagenes() {

    try {

        const response = await fetch(
            "https://picsum.photos/v2/list?limit=10"
        );

        const imagenes = await response.json();

        const galeria = document.getElementById("galeria");

        galeria.innerHTML = "";

        imagenes.forEach(imagen => {

            galeria.innerHTML += `
                <div>
                    <img src="${imagen.download_url}" width="200">
                    <p>Autor: ${imagen.author}</p>
                </div>
            `;

        });

    } catch (error) {

        console.error("Error:", error);

    }
}