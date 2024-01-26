const buttons = document.getElementsByClassName("direction")
const statusDiv = document.getElementById("status");
const baseUrl = window.location.origin + window.location.pathname

for (let button of buttons) {
    button.addEventListener("click", (e) => {
        const url = `${baseUrl}controls?command=${e.target.id}`;
        d3.json(url).then(data => statusDiv.innerHTML = data);
    });
}

