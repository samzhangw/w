document.getElementById('scoreForm').addEventListener('submit', function(event) {
    event.preventDefault();

    const chinese = document.getElementById('chinese').value.trim();
    const english = document.getElementById('english').value.trim();
    const math = document.getElementById('math').value.trim();
    const science = document.getElementById('science').value.trim();
    const social = document.getElementById('social').value.trim();
    const composition = parseInt(document.getElementById('composition').value);

    const data = {
        chinese: chinese,
        english: english,
        math: math,
        science: science,
        social: social,
        composition: composition
    };

    fetch('/calculate', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(data)
    })
    .then(response => response.json())
    .then(result => {
        document.getElementById('totalPoints').innerText = `總積分: ${result.total_points}`;
        document.getElementById('totalCredits').innerText = `總積點: ${result.total_credits}`;
        document.getElementById('eligibleSchools').innerText = `符合條件的學校: ${result.eligible_schools.join(', ')}`;
        document.getElementById('results').style.display = 'block';
    })
    .catch(error => console.error('Error:', error));
});
