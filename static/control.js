const button = document.getElementById("control");
const status_div = document.getElementById("status");
const base_url = window.location.origin + window.location.pathname

button.addEventListener("click", (e) => {
    const url = base_url + "controls?command=none";
    d3.json(url).then(data => {
        status_div.innerHTML = data;
    })
})