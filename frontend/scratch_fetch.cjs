const fs = require('fs');

async function testBackend() {
    let results = {};
    for (let i = 1; i <= 5; i++) {
        try {
            const res = await fetch('http://127.0.0.1:5000/get_all_farms_of_landlord', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ landlord_id: i })
            });
            const data = await res.json();
            results[i] = data;
        } catch (e) {
            results[i] = e.message;
        }
    }
    fs.writeFileSync('scratch_result.json', JSON.stringify(results, null, 2));
    console.log("Testing complete");
}

testBackend();
