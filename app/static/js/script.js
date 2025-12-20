document.addEventListener('DOMContentLoaded', function() {
    initTooltips();
    setupFilters();
    
    if (window.location.pathname === '/dashboard') {
        loadDashboardData();
    }
});

function initTooltips() {
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
}

function setupFilters() {
    const leagueSelect = document.getElementById('league-select');
    const teamSelect = document.getElementById('team-select');
    
    if (leagueSelect && teamSelect) {
        leagueSelect.addEventListener('change', function() {
            loadTeams(this.value);
        });
    }
}

function loadTeams(leagueId) {
    if (!leagueId) return;
    
    fetch(`/api/teams_by_league?league=${leagueId}`)
        .then(response => response.json())
        .then(data => {
            const teamSelect = document.getElementById('team-select');
            teamSelect.innerHTML = '<option value="">Todos os Times</option>';
            
            data.forEach(team => {
                const option = document.createElement('option');
                option.value = team.id;
                option.textContent = team.name;
                teamSelect.appendChild(option);
            });
        });
}

function loadDashboardData() {
    fetch('/api/top_scorers')
        .then(response => response.json())
        .then(data => {
            if (data.length > 0) {
                updateTopScorersChart(data);
            }
        });
}

function updateTopScorersChart(data) {
    const ctx = document.getElementById('topScorersChart')?.getContext('2d');
    if (!ctx) return;
    
    const chart = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: data.map(p => p.name),
            datasets: [{
                label: 'Gols',
                data: data.map(p => p.goals),
                backgroundColor: 'rgba(54, 162, 235, 0.5)',
                borderColor: 'rgba(54, 162, 235, 1)',
                borderWidth: 1
            }]
        },
        options: {
            responsive: true,
            plugins: {
                legend: {
                    display: false
                }
            }
        }
    });
}

function exportData(format) {
    const league = document.getElementById('league-select')?.value || '';
    const team = document.getElementById('team-select')?.value || '';
    
    let url = `/export/players?format=${format}`;
    if (league) url += `&league=${league}`;
    if (team) url += `&team=${team}`;
    
    window.location.href = url;
}

function comparePlayers() {
    const checkboxes = document.querySelectorAll('.player-checkbox:checked');
    const playerIds = Array.from(checkboxes).map(cb => cb.value);
    
    if (playerIds.length < 2) {
        alert('Selecione pelo menos 2 jogadores para comparar.');
        return;
    }
    
    window.location.href = `/compare?players=${playerIds.join(',')}`;
}

function searchPlayers(query) {
    if (query.length < 2) return;
    
    fetch(`/api/search?q=${query}`)
        .then(response => response.json())
        .then(data => {
            displaySearchResults(data);
        });
}

function displaySearchResults(results) {
    const container = document.getElementById('search-results');
    if (!container) return;
    
    container.innerHTML = '';
    
    if (results.length === 0) {
        container.innerHTML = '<div class="text-muted p-3">Nenhum resultado encontrado.</div>';
        return;
    }
    
    results.forEach(player => {
        const div = document.createElement('div');
        div.className = 'search-result-item p-2 border-bottom';
        div.innerHTML = `
            <a href="/player/${player.id}" class="text-decoration-none">
                <div class="d-flex justify-content-between">
                    <span>${player.name}</span>
                    <small class="text-muted">${player.team}</small>
                </div>
            </a>
        `;
        container.appendChild(div);
    });
    
    container.classList.remove('d-none');
}

function viewPlayerStats(playerId) {
    window.location.href = `/player/${playerId}`;
}

function viewTeam(teamId) {
    window.location.href = `/team/${teamId}`;
}

function manualUpdate() {
    if (confirm('Deseja atualizar os dados agora? Isso pode levar alguns minutos.')) {
        fetch('/api/update', { method: 'POST' })
            .then(response => response.json())
            .then(data => {
                alert(data.message || 'Atualização iniciada com sucesso!');
            })
            .catch(error => {
                alert('Erro ao iniciar atualização: ' + error.message);
            });
    }
}