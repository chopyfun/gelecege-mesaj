document.getElementById("messageForm").addEventListener("submit", async (e) => {
    e.preventDefault();

    const email = document.getElementById("email").value;
    const message = document.getElementById("message").value;
    const delivery_date = document.getElementById("date").value; // backend ile aynı isim

    try {
        const response = await fetch("http://127.0.0.1:5000/send", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({ email, message, delivery_date })
        });

        const result = await response.json();
        if (response.ok) {
            alert("Mesaj kaydedildi! 🎉");
            console.log("Backend yanıtı:", result);
        } else {
            alert("Hata: " + result.error);
        }
    } catch (error) {
        console.error("Bağlantı hatası:", error);
        alert("Sunucuya ulaşılamıyor!");
    }
});
