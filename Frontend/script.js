const BASE_URL = "http://127.0.0.1:5000";
function loadSummary() {
    fetch("http://127.0.0.1:5000/dashboard/summary")
    .then(res => res.json())
    .then(data => {

        document.getElementById("usersCount").innerText = data.users;
        document.getElementById("ownersCount").innerText = data.owners;
        document.getElementById("vehiclesCount").innerText = data.vehicles;
        document.getElementById("bookingsCount").innerText = data.bookings;

    });
}
function loadVehicleTypes() {
    fetch("http://127.0.0.1:5000/dashboard/vehicle-types")
    .then(res => res.json())
    .then(data => {
        let html = "<h3>Vehicle Types</h3>";

        data.forEach(item => {
            html += `<p>${item.type} : ${item.count}</p>`;
        });

        document.getElementById("dashboardData").innerHTML = html;
    });
}
function loadfrequent_users() {
    fetch("http://127.0.0.1:5000/dashboard/frequent-users")
    .then(res => res.json())
    .then(data => {

        let html = "<h3>Frequent Users</h3>";

        data.forEach(item => {
            html += `<p>${item.user_name} - ${item.bookings}</p>`;
        });

        document.getElementById("dashboardData").innerHTML = html;
    });
}
function loadCommonOwners() {
    fetch("http://127.0.0.1:5000/dashboard/common-owners")
    .then(res => res.json())
    .then(data => {
        let html = "<h3>Common Owners</h3>";

        data.forEach(item => {
            html += `<p>${item.owner_name} - ${item.vehicles}</p>`;
        });

        document.getElementById("dashboardData").innerHTML = html;
    });
}
function loadOverdueUsers() {
    fetch("http://127.0.0.1:5000/dashboard/overdue-users")
    .then(res => res.json())
    .then(data => {

        let html = "<h3>Overdue Users</h3>";

        data.forEach(item => {
            html += `<p>${item.name} - ${item.count}</p>`;
        });

        document.getElementById("dashboardData").innerHTML += html;
    });
}
function loadPendingVehicles() {
    fetch("http://127.0.0.1:5000/dashboard/pending-vehicles")
    .then(res => res.json())
    .then(data => {
        document.getElementById("pendingVehicles").innerText =
            data.pending;
    });
}
function updateDates() {
    let days = parseInt(document.getElementById("bookDays").value);

    let today = new Date();

    let lendingDate = today.toISOString().split("T")[0];

    let dueDateObj = new Date();
    dueDateObj.setDate(today.getDate() + days);
    let dueDate = dueDateObj.toISOString().split("T")[0];

    document.getElementById("lendingDate").innerText = lendingDate;
    document.getElementById("dueDate").innerText = dueDate;
    document.getElementById("bookDays").addEventListener("input", updateDates);
}
function renderTable(data, columns) {
    let table = "<table border='1' cellpadding='8' cellspacing='0'>";

    // HEADER
    table += "<tr>";
    columns.forEach(col => {
        table += `<th>${col}</th>`;
    });
    table += "</tr>";

    // ROWS
    data.forEach(item => {
        table += "<tr>";
        columns.forEach(col => {
            table += `<td>${item[col]}</td>`;
        });
        table += "</tr>";
    });

    table += "</table>";

    document.getElementById("tableContainer").innerHTML = table;
}
// ================= OWNER =================
function addOwner() {
    fetch(`${BASE_URL}/add_owner`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
            name: document.getElementById("ownerName").value,
            phone: document.getElementById("ownerPhone").value
        })
    })
    .then(res => res.json())
    .then(data => alert(data.message));
}

// ================= VEHICLE =================
function addVehicle() {
    fetch("http://127.0.0.1:5000/add_vehicle", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
            owner_id: document.getElementById("vehicleOwnerId").value,
            name: document.getElementById("vehicleName").value,
            type: document.getElementById("vehicleType").value,
            price: document.getElementById("vehiclePrice").value
        })
    })
    .then(res => res.json())
    .then(data => {
        alert(data.message);

        // ✅ CLEAR INPUTS AFTER SUCCESS
        document.getElementById("vehicleOwnerId").value = "";
        document.getElementById("vehicleName").value = "";
        document.getElementById("vehicleType").value = "";
        document.getElementById("vehiclePrice").value = "";
    });
}
// ================= USER =================
function registerUser() {
    fetch("http://127.0.0.1:5000/register_user", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
            name: document.getElementById("userName").value,
            phone: document.getElementById("userPhone").value
        })
    })
    .then(res => res.json())
    .then(data => {
        alert(data.message);

        // ✅ CLEAR FIELDS
        document.getElementById("userName").value = "";
        document.getElementById("userPhone").value = "";
    });
}

// ================= BOOK VEHICLE =================


function bookVehicle() {
    let days = parseInt(document.getElementById("bookDays").value);

    let lending_date = document.getElementById("lendingDate").innerText;
    let due_date = document.getElementById("dueDate").innerText;

    fetch("http://127.0.0.1:5000/book_vehicle", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
            user_id: document.getElementById("bookUserId").value,
            vehicle_id: document.getElementById("bookVehicleId").value,
            days: days,
            lending_date: lending_date,
            due_date: due_date
        })
    })
    .then(res => res.json())
    .then(data => {
        alert(data.message);

        document.getElementById("bookUserId").value = "";
        document.getElementById("bookVehicleId").value = "";
        document.getElementById("bookDays").value = "";
        document.getElementById("lendingDate").innerText = "";
        document.getElementById("dueDate").innerText = "";
    });
}
// ================= VIEW VEHICLES =================
function getVehicles() {
    fetch("http://127.0.0.1:5000/vehicles")
    .then(res => res.json())
    .then(data => {
        renderTable(data, [
            "vehicle_id",
            "vehicle_name",
            "type",
            "price_per_day",
            "owner_name"
        ]);
    });
}

// ================= VIEW USERS =================
function getUsers() {
    fetch("http://127.0.0.1:5000/users")
    .then(res => res.json())
    .then(data => {
        renderTable(data, ["id", "name", "phone"]);
    });
}

// ================= VIEW BOOKINGS =================
function getBookings() {
    fetch("http://127.0.0.1:5000/bookings")
    .then(res => res.json())
    .then(data => {
        renderTable(data, [
            "booking_id",
            "user_name",
            "vehicle_name",
            "lending_date",
            "due_date",
            "days"
        ]);
    });
}window.onload = function () {
    loadSummary();
    loadfrequent_users();
    loadOverdueUsers();
    loadPendingVehicles();

    getUsers();
    getOwners();
    getVehicles();
    getBookings();
};
