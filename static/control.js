const controls = document.getElementsByClassName("control")
const statusDiv = document.getElementById("status");
const baseUrl = window.location.origin + window.location.pathname

for (let control of controls) {
    control.addEventListener("click", (e) => {
        const url = `${baseUrl}controls?command=${e.target.id}`;
        d3.json(url).then(data => {
            const status = JSON.parse(data);
            statusDiv.innerHTML = status.status;
        });
    });
}

