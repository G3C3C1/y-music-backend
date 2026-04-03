// Linkin sonuna /muzik ekledik çünkü Python kodun bunu istiyor
const BASE_URL = "https://y-music-backend.onrender.com/muzik"; 

async function sarkiAra() {
    const searchInput = document.getElementById('searchQuery') || document.querySelector('input[type="text"]');
    const query = searchInput ? searchInput.value : "";
    if (!query) return;

    const resultsDiv = document.getElementById('results');
    resultsDiv.innerHTML = '<p style="color: cyan;">Aranıyor...</p>';

    try {
        // Artik link: .../muzik/ara?q=numb olacak
        const response = await fetch(`${BASE_URL}/ara?q=${encodeURIComponent(query)}`);
        const data = await response.json();

        // Senin yeni Python kodun veriyi "sonuclar" anahtarı içinde gönderiyor
        const sarkiListesi = data.sonuclar || [];

        if (sarkiListesi.length === 0) {
            resultsDiv.innerHTML = '<p style="color: yellow;">Şarkı bulunamadı Yusuf.</p>';
            return;
        }

        resultsDiv.innerHTML = '';
        sarkiListesi.forEach(video => {
            const div = document.createElement('div');
            div.style.padding = "10px";
            div.style.marginBottom = "10px";
            div.style.background = "#222";
            div.style.borderRadius = "8px";
            div.innerHTML = `
                <div style="display:flex; align-items:center; gap:10px;">
                    <img src="${video.thumbnail}" style="width:60px; border-radius:5px;">
                    <div style="flex:1;">
                        <div style="color:white; font-size:14px; font-weight:bold;">${video.title}</div>
                        <button onclick="playMusic('${video.url}', '${video.title.replace(/'/g, "\\")}')" 
                                style="background:#00ff00; color:black; border:none; padding:5px 12px; margin-top:5px; border-radius:4px; font-weight:bold;">
                            Oynat
                        </button>
                    </div>
                </div>
            `;
            resultsDiv.appendChild(div);
        });

    } catch (error) {
        resultsDiv.innerHTML = '<p style="color: red;">Bağlantı Hatası!</p>';
        console.error(error);
    }
}

function playMusic(audioUrl, title) {
    const player = document.getElementById('audioPlayer');
    const source = document.getElementById('audioSource');
    const titleDisplay = document.getElementById('currentTitle');

    if (player && source) {
        source.src = audioUrl; // Yeni kodun doğrudan ses linkini (URL) veriyor
        if (titleDisplay) titleDisplay.innerText = "Çalıyor: " + title;
        player.load();
        player.play();
    }
}
