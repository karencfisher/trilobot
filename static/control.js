const up_arrow = document.getElementById("up");
const left_arrow = document.getElementById("left");
const stop_button = document.getElementById("stop");
const right_arrow = document.getElementById("right");
const down_arrow = document.getElementById("down");
const status_div = document.getElementById("status");
const base_url = window.location.origin + window.location.pathname

up_arrow.addEventListener("click", (e) => {
    const url = base_url + "controls?command=forward";
    d3.json(url).then(data => {
        status_div.innerHTML = data;
    })
});

left_arrow.addEventListener("click", (e) => {
    const url = base_url + "controls?command=left";
    d3.json(url).then(data => {
        status_div.innerHTML = data;
    })
});

stop_button.addEventListener("click", (e) => {
    const url = base_url + "controls?command=stop";
    d3.json(url).then(data => {
        status_div.innerHTML = data;
    })
});

right_arrow.addEventListener("click", (e) => {
    const url = base_url + "controls?command=right";
    d3.json(url).then(data => {
        status_div.innerHTML = data;
    })
});

down_arrow.addEventListener("click", (e) => {
    const url = base_url + "controls?command=reverse";
    d3.json(url).then(data => {
        status_div.innerHTML = data;
    })
});