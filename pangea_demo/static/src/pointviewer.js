let viewRotation = 0.0;
let viewDistance = 2.0;
let viewFocalLength = 50.0;
let pointData;


// TODO: Bind arrow keys to rotate left and right and up down to change camera distance, maybe +/- for focal length
let leftTurn = document.getElementById("left-turn");
leftTurn.onclick = (event) => {
    viewRotation-=0.1;
    setText('rotation', viewRotation);
    renderImage().then();
    event.preventDefault();
};

let rightTurn = document.getElementById("right-turn");
rightTurn.onclick = (event) => {
    viewRotation+=0.1;
    setText('rotation', viewRotation);
    renderImage().then();
    event.preventDefault();
};

window.addEventListener("keydown", function (event) {
    if (event.defaultPrevented) {
        return;
    }

    switch (event.key) {
        case "Left":
        case "ArrowLeft":
            viewRotation-=0.1;
            setText('rotation', viewRotation);
            renderImage().then();
            break;
        case "Right":
        case "ArrowRight":
            viewRotation+=0.1;
            setText('rotation', viewRotation);
            renderImage().then();
            break;
        case "Up":
        case "ArrowUp":
            viewDistance+=0.1;
            setText('distance', viewDistance);
            renderImage().then();
            break;
        case "Down":
        case "ArrowDown":
            viewDistance-=0.1;
            setText('distance', viewDistance)
            renderImage().then();
            break;
        case "Minus":
        case "Dash":
            viewFocalLength-=0.1;
            setText('focal_length', viewFocalLength);
            renderImage().then();
            break;
    }

  event.preventDefault();
}, true);


let viewParams = document.querySelectorAll('.view');
viewParams.forEach(el => {
    el.onchange = () => renderImage();
});

async function renderImage() {
    viewRotation = Number(document.getElementById('rotation').value);
    viewDistance = Number(document.getElementById('distance').value);
    viewFocalLength = Number(document.getElementById('focal_length').value);

    const url = getUrl("/api/render")
    const data = {
        'points': pointData,
        'params': {
                "rotation": viewRotation,
                "distance": viewDistance,
                "focal_length": viewFocalLength
            }
        }

    const options = {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(data)
    }

    fetch(url, options)
        .then((response) => response.blob())
        .then(imageBlob => {
            document.getElementById("render-image").src = URL.createObjectURL(imageBlob);
  })

}

function getUrl(path) {
    let host = document.URL;
    if (host.endsWith('/')) path = path.substring(1);
    return host + path
}

function setText(id, value) {
    let el = document.getElementById(id);
    el.value = value;
}

async function loadData() {
    setText('rotation', viewRotation);
    setText('distance', viewDistance);
    setText('focal_length', viewFocalLength);

    // TODO: load /data/points.json into pointData
    // TODO: connect dataSelect to different point datasets. Either add data to points.json or load multiple points
    //  files
}


