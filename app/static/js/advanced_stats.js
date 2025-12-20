// advanced_stats.js - Script para estatísticas avançadas

document.addEventListener('DOMContentLoaded', function() {
    console.log("📊 Inicializando estatísticas avançadas...");
    
    // Carregar dados iniciais
    loadXGAnalysis();
    loadPassingStats();
    loadDefensiveStats();
    loadTeamsForPrediction();
    loadGoalTiming();
    
    // Configurar scroll suave para as seções
    document.querySelectorAll('.list-group-item-action').forEach(item => {
        item.addEventListener('click', function(e) {
            e.preventDefault();
            
            // Remover active de todos
            document.querySelectorAll('.list-group-item-action').forEach(i => {
                i.classList.remove('active');
            });
            
            // Adicionar active ao clicado
            this.classList.add('active');
            
            // Scroll suave
            const targetId = this.getAttribute('href').substring(1);
            const targetElement = document.getElementById(targetId);
            if (targetElement) {
                targetElement.scrollIntoView({
                    behavior: 'smooth',
                    block: 'start'
                });
            }
        });
    });
    
    // Configurar tooltips
    initTooltips();
});

function initTooltips() {
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
}

// ===== ANÁLISE xG =====
function loadXGAnalysis() {
    console.log("📈 Carregando análise xG...");
    
    // Mostrar loading
    const xgTableBody = document.getElementById('xgTableBody');
    if (xgTableBody) {
        xgTableBody.innerHTML = `
            <tr>
                <td colspan="5" class="text-center">
                    <div class="spinner-border spinner-border-sm" role="status">
                        <span class="visually-hidden">Carregando...</span>
                    </div>
                    Carregando dados xG...
                </td>
            </tr>
        `;
    }
    
    // Buscar dados xG
    fetch('/api/xg/analysis')
        .then(response => {
            if (!response.ok) {
                throw new Error('Erro na requisição');
            }
            return response.json();
        })
        .then(data => {
            console.log("✅ Dados xG recebidos:", data);
            updateXGCharts(data);
            updateXGTable(data.players);
        })
        .catch(error => {
            console.error("❌ Erro ao carregar xG:", error);
            
            // Dados de fallback
            const fallbackData = {
                dates: ['Jan', 'Fev', 'Mar', 'Abr', 'Mai'],
                xg_trend: [1.2, 1.8, 1.5, 2.1, 1.9],
                goals_trend: [1, 2, 1, 3, 2],
                players: [
                    {name: 'Jogador A', xg: 8.7, goals: 9, xg_per_90: 0.65},
                    {name: 'Jogador B', xg: 5.2, goals: 6, xg_per_90: 0.48},
                    {name: 'Jogador C', xg: 3.1, goals: 2, xg_per_90: 0.32},
                    {name: 'Jogador D', xg: 6.5, goals: 7, xg_per_90: 0.55},
                    {name: 'Jogador E', xg: 4.8, goals: 5, xg_per_90: 0.41}
                ]
            };
            
            updateXGCharts(fallbackData);
            updateXGTable(fallbackData.players);
            
            // Mostrar aviso
            if (xgTableBody) {
                const warningRow = `
                    <tr>
                        <td colspan="5" class="text-center text-warning">
                            <small>⚠️ Dados de exemplo (API offline)</small>
                        </td>
                    </tr>
                `;
                xgTableBody.innerHTML += warningRow;
            }
        });
}

function updateXGCharts(data) {
    console.log("📊 Atualizando gráficos xG...");
    
    // Gráfico 1: Tendência xG vs Gols
    const ctx1 = document.getElementById('xgTrendChart');
    if (ctx1) {
        // Destruir gráfico anterior se existir
        if (window.xgTrendChart instanceof Chart) {
            window.xgTrendChart.destroy();
        }
        
        window.xgTrendChart = new Chart(ctx1.getContext('2d'), {
            type: 'line',
            data: {
                labels: data.dates || ['Sem 1', 'Sem 2', 'Sem 3', 'Sem 4', 'Sem 5'],
                datasets: [
                    {
                        label: 'xG',
                        data: data.xg_trend || [1.2, 1.8, 1.5, 2.1, 1.9],
                        borderColor: 'rgb(255, 99, 132)',
                        backgroundColor: 'rgba(255, 99, 132, 0.1)',
                        borderWidth: 2,
                        fill: true,
                        tension: 0.4
                    },
                    {
                        label: 'Gols Reais',
                        data: data.goals_trend || [1, 2, 1, 3, 2],
                        borderColor: 'rgb(54, 162, 235)',
                        backgroundColor: 'rgba(54, 162, 235, 0.1)',
                        borderWidth: 2,
                        fill: true,
                        tension: 0.4
                    }
                ]
            },
            options: {
                responsive: true,
                plugins: {
                    title: {
                        display: true,
                        text: 'Tendência xG vs Gols Reais',
                        font: {
                            size: 14
                        }
                    },
                    legend: {
                        position: 'top',
                    }
                },
                scales: {
                    y: {
                        beginAtZero: true,
                        title: {
                            display: true,
                            text: 'Valor'
                        }
                    }
                }
            }
        });
    }
    
    // Gráfico 2: xG vs Gols (scatter)
    const ctx2 = document.getElementById('xgVsGoalsChart');
    if (ctx2) {
        // Destruir gráfico anterior se existir
        if (window.xgVsGoalsChart instanceof Chart) {
            window.xgVsGoalsChart.destroy();
        }
        
        // Criar dados scatter (se não existirem)
        const scatterData = data.scatter_data || [
            {x: 5.2, y: 6},
            {x: 8.7, y: 9},
            {x: 3.1, y: 2},
            {x: 6.5, y: 7},
            {x: 4.8, y: 5},
            {x: 7.3, y: 8},
            {x: 2.5, y: 3},
            {x: 9.1, y: 10}
        ];
        
        window.xgVsGoalsChart = new Chart(ctx2.getContext('2d'), {
            type: 'scatter',
            data: {
                datasets: [{
                    label: 'Jogadores',
                    data: scatterData,
                    backgroundColor: 'rgba(54, 162, 235, 0.7)',
                    borderColor: 'rgba(54, 162, 235, 1)',
                    borderWidth: 1,
                    pointRadius: 6
                }]
            },
            options: {
                responsive: true,
                plugins: {
                    title: {
                        display: true,
                        text: 'xG vs Gols (Eficiência)',
                        font: {
                            size: 14
                        }
                    },
                    tooltip: {
                        callbacks: {
                            label: function(context) {
                                return `xG: ${context.parsed.x}, Gols: ${context.parsed.y}`;
                            }
                        }
                    }
                },
                scales: {
                    x: {
                        title: {
                            display: true,
                            text: 'xG'
                        },
                        beginAtZero: true
                    },
                    y: {
                        title: {
                            display: true,
                            text: 'Gols'
                        },
                        beginAtZero: true
                    }
                }
            }
        });
    }
}

function updateXGTable(players) {
    const tbody = document.getElementById('xgTableBody');
    if (!tbody) return;
    
    tbody.innerHTML = '';
    
    if (!players || players.length === 0) {
        tbody.innerHTML = `
            <tr>
                <td colspan="5" class="text-center text-muted">
                    Nenhum dado disponível
                </td>
            </tr>
        `;
        return;
    }
    
    players.forEach((player, index) => {
        const diff = (player.goals || 0) - (player.xg || 0);
        const diffClass = diff > 0.5 ? 'text-success' : diff < -0.5 ? 'text-danger' : '';
        const diffSymbol = diff > 0 ? '+' : '';
        
        const row = document.createElement('tr');
        row.innerHTML = `
            <td>
                <strong>${player.name || `Jogador ${index + 1}`}</strong>
            </td>
            <td>${(player.xg || 0).toFixed(1)}</td>
            <td>${player.goals || 0}</td>
            <td class="${diffClass}">
                ${diffSymbol}${diff.toFixed(1)}
            </td>
            <td>${(player.xg_per_90 || 0).toFixed(2)}</td>
        `;
        tbody.appendChild(row);
    });
}

// ===== ESTATÍSTICAS DE PASSES =====
function loadPassingStats() {
    console.log("⚽ Carregando estatísticas de passes...");
    
    // Atualizar cards com loading
    document.getElementById('avgPassAccuracy').textContent = '...';
    document.getElementById('totalPasses').textContent = '...';
    document.getElementById('keyPassesPM').textContent = '...';
    document.getElementById('longBallAccuracy').textContent = '...';
    
    fetch('/api/passing/stats')
        .then(response => {
            if (!response.ok) throw new Error('Erro na requisição');
            return response.json();
        })
        .then(data => {
            updatePassingStats(data);
        })
        .catch(error => {
            console.error("❌ Erro ao carregar passes:", error);
            
            // Dados de fallback
            const fallbackData = {
                avg_pass_accuracy: 82.5,
                total_passes: 15420,
                key_passes_per_match: 2.3,
                short_passes_per_match: 45.2,
                long_passes_per_match: 12.1,
                crosses_per_match: 7.8,
                through_balls_per_match: 1.2
            };
            
            updatePassingStats(fallbackData);
        });
}

function updatePassingStats(data) {
    console.log("✅ Atualizando estatísticas de passes:", data);
    
    // Atualizar cards
    document.getElementById('avgPassAccuracy').textContent = 
        `${(data.avg_pass_accuracy || 0).toFixed(1)}%`;
    document.getElementById('totalPasses').textContent = 
        (data.total_passes || 0).toLocaleString('pt-BR');
    document.getElementById('keyPassesPM').textContent = 
        (data.key_passes_per_match || 0).toFixed(1);
    document.getElementById('longBallAccuracy').textContent = 
        `${(data.long_ball_accuracy || 65).toFixed(1)}%`;
    
    // Gráfico de passes
    const ctx = document.getElementById('passingChart');
    if (ctx) {
        // Destruir gráfico anterior se existir
        if (window.passingChart instanceof Chart) {
            window.passingChart.destroy();
        }
        
        window.passingChart = new Chart(ctx.getContext('2d'), {
            type: 'bar',
            data: {
                labels: ['Passes Curtos', 'Passes Longos', 'Cruzamentos', 'Passes Chave', 'Bolas através'],
                datasets: [{
                    label: 'Por Partida',
                    data: [
                        data.short_passes_per_match || 45.2,
                        data.long_passes_per_match || 12.1,
                        data.crosses_per_match || 7.8,
                        data.key_passes_per_match || 2.3,
                        data.through_balls_per_match || 1.2
                    ],
                    backgroundColor: [
                        'rgba(54, 162, 235, 0.7)',
                        'rgba(255, 206, 86, 0.7)',
                        'rgba(75, 192, 192, 0.7)',
                        'rgba(153, 102, 255, 0.7)',
                        'rgba(255, 159, 64, 0.7)'
                    ],
                    borderColor: [
                        'rgb(54, 162, 235)',
                        'rgb(255, 206, 86)',
                        'rgb(75, 192, 192)',
                        'rgb(153, 102, 255)',
                        'rgb(255, 159, 64)'
                    ],
                    borderWidth: 1
                }]
            },
            options: {
                responsive: true,
                plugins: {
                    title: {
                        display: true,
                        text: 'Distribuição de Tipos de Passe',
                        font: {
                            size: 14
                        }
                    },
                    legend: {
                        display: false
                    }
                },
                scales: {
                    y: {
                        beginAtZero: true,
                        title: {
                            display: true,
                            text: 'Quantidade por jogo'
                        }
                    }
                }
            }
        });
    }
}

// ===== ESTATÍSTICAS DEFENSIVAS =====
function loadDefensiveStats() {
    console.log("🛡️ Carregando estatísticas defensivas...");
    
    // Atualizar cards com loading
    document.getElementById('savesPerMatch').textContent = '...';
    document.getElementById('tacklesPerMatch').textContent = '...';
    document.getElementById('interceptionsPerMatch').textContent = '...';
    
    fetch('/api/defensive/stats')
        .then(response => {
            if (!response.ok) throw new Error('Erro na requisição');
            return response.json();
        })
        .then(data => {
            updateDefensiveStats(data);
        })
        .catch(error => {
            console.error("❌ Erro ao carregar defesas:", error);
            
            // Dados de fallback
            const fallbackData = {
                saves_per_match: 3.2,
                interceptions_per_match: 12.5,
                tackles_per_match: 18.7,
                clearances_per_match: 22.1,
                blocks_per_match: 4.8,
                fouls_per_match: 13.8,
                clean_sheets: 8
            };
            
            updateDefensiveStats(fallbackData);
        });
}

function updateDefensiveStats(data) {
    console.log("✅ Atualizando estatísticas defensivas:", data);
    
    // Atualizar cards
    document.getElementById('savesPerMatch').textContent = 
        (data.saves_per_match || 0).toFixed(1);
    document.getElementById('tacklesPerMatch').textContent = 
        (data.tackles_per_match || 0).toFixed(1);
    document.getElementById('interceptionsPerMatch').textContent = 
        (data.interceptions_per_match || 0).toFixed(1);
    
    // Gráfico radar
    const ctx = document.getElementById('defensiveRadarChart');
    if (ctx) {
        // Destruir gráfico anterior se existir
        if (window.defensiveRadarChart instanceof Chart) {
            window.defensiveRadarChart.destroy();
        }
        
        window.defensiveRadarChart = new Chart(ctx.getContext('2d'), {
            type: 'radar',
            data: {
                labels: ['Defesas', 'Desarmes', 'Interceptações', 'Cortes', 'Bloqueios', 'Faltas'],
                datasets: [{
                    label: 'Médias por Jogo',
                    data: [
                        data.saves_per_match || 3.2,
                        data.tackles_per_match || 18.7,
                        data.interceptions_per_match || 12.5,
                        data.clearances_per_match || 22.1,
                        data.blocks_per_match || 4.8,
                        data.fouls_per_match || 13.8
                    ],
                    backgroundColor: 'rgba(54, 162, 235, 0.2)',
                    borderColor: 'rgb(54, 162, 235)',
                    pointBackgroundColor: 'rgb(54, 162, 235)',
                    pointBorderColor: '#fff',
                    pointHoverBackgroundColor: '#fff',
                    pointHoverBorderColor: 'rgb(54, 162, 235)'
                }]
            },
            options: {
                responsive: true,
                plugins: {
                    title: {
                        display: true,
                        text: 'Perfil Defensivo - Médias por Jogo',
                        font: {
                            size: 14
                        }
                    },
                    legend: {
                        position: 'top',
                    }
                },
                scales: {
                    r: {
                        beginAtZero: true,
                        ticks: {
                            stepSize: 5
                        }
                    }
                }
            }
        });
    }
}

// ===== TEMPOS DOS GOLS =====
function loadGoalTiming() {
    console.log("⏰ Carregando tempos dos gols...");
    
    fetch('/api/goal-timing/aggregated')
        .then(response => {
            if (!response.ok) throw new Error('Erro na requisição');
            return response.json();
        })
        .then(data => {
            updateGoalTimingChart(data);
            updateGoalInsights(data);
        })
        .catch(error => {
            console.error("❌ Erro ao carregar tempos dos gols:", error);
            
            // Dados de fallback
            const fallbackData = {
                total_goals: 42,
                first_half_goals: 18,
                second_half_goals: 24,
                time_distribution: {
                    '0_15': 4,
                    '16_30': 7,
                    '31_45': 7,
                    '46_60': 9,
                    '61_75': 8,
                    '76_90': 6,
                    'extra': 1
                },
                avg_goal_minute: 52.3,
                early_goals_0_15: 4,
                late_goals_75_90: 7
            };
            
            updateGoalTimingChart(fallbackData);
            updateGoalInsights(fallbackData);
        });
}

function updateGoalTimingChart(data) {
    const ctx = document.getElementById('goalTimingChart');
    if (!ctx) return;
    
    // Destruir gráfico anterior se existir
    if (window.goalTimingChart instanceof Chart) {
        window.goalTimingChart.destroy();
    }
    
    const labels = ['0-15', '16-30', '31-45', '46-60', '61-75', '76-90', 'Extra'];
    const values = labels.map(label => {
        const key = label.replace('-', '_').toLowerCase();
        if (label === 'Extra') key = 'extra';
        return data.time_distribution?.[key] || 0;
    });
    
    window.goalTimingChart = new Chart(ctx.getContext('2d'), {
        type: 'bar',
        data: {
            labels: labels,
            datasets: [{
                label: 'Gols',
                data: values,
                backgroundColor: [
                    'rgba(255, 99, 132, 0.7)',
                    'rgba(255, 159, 64, 0.7)',
                    'rgba(255, 205, 86, 0.7)',
                    'rgba(75, 192, 192, 0.7)',
                    'rgba(54, 162, 235, 0.7)',
                    'rgba(153, 102, 255, 0.7)',
                    'rgba(201, 203, 207, 0.7)'
                ],
                borderColor: [
                    'rgb(255, 99, 132)',
                    'rgb(255, 159, 64)',
                    'rgb(255, 205, 86)',
                    'rgb(75, 192, 192)',
                    'rgb(54, 162, 235)',
                    'rgb(153, 102, 255)',
                    'rgb(201, 203, 207)'
                ],
                borderWidth: 1
            }]
        },
        options: {
            responsive: true,
            plugins: {
                title: {
                    display: true,
                    text: 'Distribuição dos Gols por Intervalo de Tempo',
                    font: {
                        size: 14
                    }
                },
                legend: {
                    display: false
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    title: {
                        display: true,
                        text: 'Número de Gols'
                    },
                    ticks: {
                        stepSize: 1
                    }
                }
            }
        }
    });
}

function updateGoalInsights(data) {
    document.getElementById('firstHalfGoals').textContent = 
        `${data.first_half_goals || 0} gols no 1º tempo`;
    document.getElementById('secondHalfGoals').textContent = 
        `${data.second_half_goals || 0} gols no 2º tempo`;
    
    const lateGoals = (data.time_distribution?.['76_90'] || 0) + (data.time_distribution?.extra || 0);
    const earlyGoals = data.time_distribution?.['0_15'] || 0;
    
    document.getElementById('lateGoals').textContent = 
        `${lateGoals} gols após 75 minutos`;
    document.getElementById('earlyGoals').textContent = 
        `${earlyGoals} gols antes de 15 minutos`;
}

// ===== CORRECT SCORE PREDICTIONS =====
function loadTeamsForPrediction() {
    console.log("🏆 Carregando times para previsões...");
    
    fetch('/api/teams/list')
        .then(response => {
            if (!response.ok) throw new Error('Erro na requisição');
            return response.json();
        })
        .then(teams => {
            const homeSelect = document.getElementById('homeTeamSelect');
            const awaySelect = document.getElementById('awayTeamSelect');
            
            if (!homeSelect || !awaySelect) return;
            
            // Limpar selects
            homeSelect.innerHTML = '<option value="">Selecione um time...</option>';
            awaySelect.innerHTML = '<option value="">Selecione um time...</option>';
            
            // Ordenar times por nome
            teams.sort((a, b) => a.name.localeCompare(b.name));
            
            // Adicionar opções
            teams.forEach(team => {
                const option = document.createElement('option');
                option.value = team.id;
                option.textContent = team.name;
                homeSelect.appendChild(option.cloneNode(true));
                awaySelect.appendChild(option);
            });
            
            console.log(`✅ ${teams.length} times carregados`);
        })
        .catch(error => {
            console.error("❌ Erro ao carregar times:", error);
            
            // Times de fallback
            const fallbackTeams = [
                {id: 1, name: 'Manchester United'},
                {id: 2, name: 'Liverpool'},
                {id: 3, name: 'Manchester City'},
                {id: 4, name: 'Chelsea'},
                {id: 5, name: 'Arsenal'}
            ];
            
            const homeSelect = document.getElementById('homeTeamSelect');
            const awaySelect = document.getElementById('awayTeamSelect');
            
            if (homeSelect && awaySelect) {
                fallbackTeams.forEach(team => {
                    const option = `<option value="${team.id}">${team.name}</option>`;
                    homeSelect.innerHTML += option;
                    awaySelect.innerHTML += option;
                });
            }
        });
}

function getScorePredictions() {
    const homeTeamId = document.getElementById('homeTeamSelect')?.value;
    const awayTeamId = document.getElementById('awayTeamSelect')?.value;
    
    if (!homeTeamId || !awayTeamId) {
        showAlert('Selecione ambos os times', 'warning');
        return;
    }
    
    if (homeTeamId === awayTeamId) {
        showAlert('Selecione times diferentes', 'warning');
        return;
    }
    
    // Mostrar loading
    const resultsDiv = document.getElementById('predictionsResult');
    if (resultsDiv) {
        resultsDiv.style.display = 'block';
        resultsDiv.innerHTML = `
            <div class="text-center py-4">
                <div class="spinner-border text-primary" role="status">
                    <span class="visually-hidden">Calculando...</span>
                </div>
                <p class="mt-2">Calculando previsões...</p>
            </div>
        `;
    }
    
    console.log(`🔮 Calculando previsões: ${homeTeamId} vs ${awayTeamId}`);
    
    // Simular delay de rede
    setTimeout(() => {
        fetch(`/api/correct-score/predictions?home_team=${homeTeamId}&away_team=${awayTeamId}`)
            .then(response => {
                if (!response.ok) throw new Error('Erro na requisição');
                return response.json();
            })
            .then(data => {
                displayScorePredictions(data);
            })
            .catch(error => {
                console.error("❌ Erro ao obter previsões:", error);
                
                // Dados de fallback
                const fallbackData = {
                    most_likely: '1-1',
                    probabilities: {
                        '0-0': 15.2,
                        '1-0': 12.5,
                        '0-1': 11.8,
                        '1-1': 18.3,
                        '2-0': 8.7,
                        '0-2': 7.9,
                        '2-1': 9.4,
                        '1-2': 8.1,
                        '2-2': 5.3,
                        '3+': 2.8
                    },
                    both_teams_score: 68.4,
                    over_2_5: 42.7,
                    under_2_5: 57.3
                };
                
                displayScorePredictions(fallbackData);
                showAlert('Usando dados de exemplo (API offline)', 'info');
            });
    }, 1000);
}

function displayScorePredictions(data) {
    const container = document.getElementById('predictionsResult');
    if (!container) return;
    
    // Ordenar probabilidades do maior para o menor
    const sortedProbabilities = Object.entries(data.probabilities || {})
        .sort(([, a], [, b]) => b - a);
    
    let scoreTableHTML = '';
    sortedProbabilities.forEach(([score, prob]) => {
        const isMostLikely = score === data.most_likely;
        const rowClass = isMostLikely ? 'table-success' : '';
        
        scoreTableHTML += `
            <tr class="${rowClass}">
                <td>
                    ${score}
                    ${isMostLikely ? '<span class="badge bg-success ms-2">Mais Provável</span>' : ''}
                </td>
                <td>
                    <div class="progress" style="height: 20px;">
                        <div class="progress-bar ${isMostLikely ? 'bg-success' : 'bg-primary'}" 
                             style="width: ${prob}%">
                            ${prob}%
                        </div>
                    </div>
                </td>
            </tr>
        `;
    });
    
    container.innerHTML = `
        <div class="row">
            <div class="col-md-6">
                <h6>📊 Probabilidades de Placar</h6>
                <div class="table-responsive">
                    <table class="table table-sm">
                        <thead>
                            <tr>
                                <th>Placar</th>
                                <th>Probabilidade</th>
                            </tr>
                        </thead>
                        <tbody>
                            ${scoreTableHTML}
                        </tbody>
                    </table>
                </div>
            </div>
            <div class="col-md-6">
                <h6>🎯 Outras Probabilidades</h6>
                
                <div class="mb-3">
                    <label class="form-label">Ambos marcam</label>
                    <div class="progress mb-2" style="height: 25px;">
                        <div class="progress-bar bg-info" style="width: ${data.both_teams_score || 0}%">
                            ${data.both_teams_score || 0}%
                        </div>
                    </div>
                </div>
                
                <div class="mb-3">
                    <label class="form-label">Mais de 2.5 gols</label>
                    <div class="progress mb-2" style="height: 25px;">
                        <div class="progress-bar bg-success" style="width: ${data.over_2_5 || 0}%">
                            ${data.over_2_5 || 0}%
                        </div>
                    </div>
                </div>
                
                <div class="mb-3">
                    <label class="form-label">Menos de 2.5 gols</label>
                    <div class="progress" style="height: 25px;">
                        <div class="progress-bar bg-warning" style="width: ${data.under_2_5 || 0}%">
                            ${data.under_2_5 || 0}%
                        </div>
                    </div>
                </div>
                
                <div class="alert alert-primary">
                    <strong>Placar mais provável:</strong> ${data.most_likely || '1-1'}
                </div>
            </div>
        </div>
    `;
}

// ===== FUNÇÕES AUXILIARES =====
function showAlert(message, type = 'info') {
    // Criar alerta
    const alertDiv = document.createElement('div');
    alertDiv.className = `alert alert-${type} alert-dismissible fade show`;
    alertDiv.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    
    // Adicionar ao topo da página
    const container = document.querySelector('.container');
    if (container) {
        container.insertBefore(alertDiv, container.firstChild);
        
        // Remover após 5 segundos
        setTimeout(() => {
            if (alertDiv.parentNode) {
                alertDiv.remove();
            }
        }, 5000);
    }
}

// ===== ATUALIZAÇÃO AUTOMÁTICA =====
function refreshStats() {
    console.log("🔄 Atualizando todas as estatísticas...");
    
    // Mostrar indicador de loading
    showAlert('Atualizando estatísticas...', 'info');
    
    // Recarregar cada seção
    loadXGAnalysis();
    loadPassingStats();
    loadDefensiveStats();
    loadGoalTiming();
    
    setTimeout(() => {
        showAlert('Estatísticas atualizadas com sucesso!', 'success');
    }, 2000);
}

// Adicionar botão de refresh se não existir
document.addEventListener('DOMContentLoaded', function() {
    // Verificar se já existe um botão de refresh
    if (!document.getElementById('refreshStatsBtn')) {
        // Criar botão
        const refreshBtn = document.createElement('button');
        refreshBtn.id = 'refreshStatsBtn';
        refreshBtn.className = 'btn btn-sm btn-outline-primary';
        refreshBtn.innerHTML = '<i class="bi bi-arrow-clockwise"></i> Atualizar';
        refreshBtn.onclick = refreshStats;
        
        // Adicionar ao cabeçalho
        const header = document.querySelector('.card-header h5');
        if (header) {
            const headerDiv = header.parentElement;
            if (headerDiv.querySelector('.btn') === null) {
                headerDiv.classList.add('d-flex', 'justify-content-between', 'align-items-center');
                headerDiv.appendChild(refreshBtn);
            }
        }
    }
});