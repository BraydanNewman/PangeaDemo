let viewRotation = 0.0;
let viewDistance = 2.0;
let viewFocalLength = 50.0;
let pointData = {};

const radioButtons = document.querySelectorAll('input[name="point-data"]');
        for(const radioButton of radioButtons){
            radioButton.addEventListener('change', () => renderImage().then());
        }

let leftTurn = document.getElementById("left-turn");
leftTurn.onclick = (event) => {
    viewRotation -= 0.1;
    setText('rotation', viewRotation);
    renderImage().then();
    event.preventDefault();
};

let rightTurn = document.getElementById("right-turn");
rightTurn.onclick = (event) => {
    viewRotation += 0.1;
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
            viewRotation -= 0.1;
            setText('rotation', viewRotation);
            break;
        case "Right":
        case "ArrowRight":
            viewRotation += 0.1;
            setText('rotation', viewRotation);
            break;
        case "Up":
        case "ArrowUp":
            viewDistance += 0.1;
            setText('distance', viewDistance);
            break;
        case "Down":
        case "ArrowDown":
            viewDistance -= 0.1;
            setText('distance', viewDistance)
            break;
        case "+":
            viewFocalLength+=0.1;
            setText('focal_length', viewFocalLength)
            break;
        case "-":
            viewFocalLength-=0.1;
            setText('focal_length', viewFocalLength)
    }
    renderImage().then();

    event.preventDefault();
}, true);


let viewParams = document.querySelectorAll('.view');
viewParams.forEach(el => {
    el.onchange = () => renderImage();
});

async function renderImage() {
    await loadData()

    viewRotation = Number(document.getElementById('rotation').value);
    viewDistance = Number(document.getElementById('distance').value);
    viewFocalLength = Number(document.getElementById('focal_length').value);

    const options = {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            points: pointData,
            'params': {
                "rotation": viewRotation,
                "distance": viewDistance,
                "focal_length": viewFocalLength
            }
        })
    }

    fetch(getUrl("/api/render"), options)
        .then((response) => response.blob())
        .then(imageBlob => {
            document.getElementById("render-image").src = URL.createObjectURL(imageBlob);
        })
        .catch(error => {
            console.log(error);
            document.getElementById("render-image").src = '/img/black.png';
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

    await fetch(getUrl('/data/points.json'))
        .then(response =>
            response.json()
        )
        .then(data => {
            const dataSelectors = document.querySelectorAll('input[name="point-data"]');
            let selectedData;
            for (const dataSelector of dataSelectors) {
                if (dataSelector.checked) {
                    selectedData = dataSelector.value;
                    break;
                }
            }
            const dataSets = []
            for (let set in data) {
                dataSets.push(data[set])
            }
            console.log(dataSets[selectedData-1])
            return pointData = dataSets[selectedData-1]
        })
}


