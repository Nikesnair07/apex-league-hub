// Apex League Hub - Main Application Controller (Static Browser Version)

(function () {
  const {
    initialTeams,
    initialPlayers,
    initialCoaches,
    initialMatches,
    initialVenues,
    initialReferees,
    initialBracketData
  } = window.ApexData;

  // Reactive App State
  let state = {
    activeScreen: 'landing', // 'landing', 'login', 'app'
    activeSubView: 'dashboard',
    userRole: 'Administrator',
    teams: [...initialTeams],
    players: [...initialPlayers],
    coaches: [...initialCoaches],
    matches: [...initialMatches],
    venues: [...initialVenues],
    referees: [...initialReferees],
    bracket: JSON.parse(JSON.stringify(initialBracketData)),
    tournaments: (() => { try { return JSON.parse(localStorage.getItem('apexLeagueTournaments') || '[]'); } catch (_) { return []; } })(),
    playersFilter: { team: 'ALL', position: 'ALL', query: '' },
    matchFilter: 'ALL'
  };

  // Backend API Configuration (Decoupled & Production-Ready)
  const API_BASE = (window.__APEX_CONFIG__ && window.__APEX_CONFIG__.API_BASE)
    ? window.__APEX_CONFIG__.API_BASE.replace(/\/+$/, '')
    : (window.location.origin && window.location.origin.includes(':8000'))
      ? '/api'
      : (window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1')
        ? 'http://127.0.0.1:8000/api'
        : '/api';
  let isBackendConnected = false;

  // Chart instances storage for destruction/re-render
  let chartInstances = {};

  // DOM Ready Initialization
  document.addEventListener('DOMContentLoaded', () => {
    initEventListeners();
    updateLandingStats();
    updateApiDocsLink();
    renderAllViews();
    checkAndSyncBackend();
  });

  // ==========================================
  // NAVIGATION & EVENT LISTENERS
  // ==========================================
  function initEventListeners() {
    // Screen Switching (Landing -> Login -> App)
    document.getElementById('landing-login-btn')?.addEventListener('click', () => switchScreen('login'));
    document.getElementById('landing-dash-btn')?.addEventListener('click', () => switchScreen('app'));
    document.getElementById('hero-get-started')?.addEventListener('click', () => switchScreen('login'));
    document.getElementById('hero-view-demo')?.addEventListener('click', () => switchScreen('app'));
    document.getElementById('back-to-landing')?.addEventListener('click', () => switchScreen('landing'));
    document.getElementById('sidebar-logout-btn')?.addEventListener('click', () => switchScreen('login'));
    document.getElementById('backend-status-pill')?.addEventListener('click', () => checkAndSyncBackend());

    // Role Selector on Login Page
    document.querySelectorAll('.role-btn').forEach(btn => {
      btn.addEventListener('click', (e) => {
        document.querySelectorAll('.role-btn').forEach(b => b.classList.remove('active'));
        e.currentTarget.classList.add('active');
        state.userRole = e.currentTarget.dataset.role;
        document.getElementById('active-user-role').textContent = state.userRole;
      });
    });

    // Login Form Submit
    document.getElementById('login-form')?.addEventListener('submit', (e) => {
      e.preventDefault();
      switchScreen('app');
    });

    // Sidebar Subview Navigation
    document.querySelectorAll('.menu-item').forEach(item => {
      item.addEventListener('click', (e) => {
        e.preventDefault();
        const view = item.dataset.view;
        if (view) {
          switchSubView(view);
        }
      });
    });

    // Sidebar Collapse Toggle
    const sidebar = document.getElementById('sidebar');
    document.getElementById('sidebar-toggle-btn')?.addEventListener('click', () => {
      sidebar.classList.toggle('collapsed');
    });

    // Mobile Menu Toggle
    document.getElementById('mobile-menu-trigger')?.addEventListener('click', () => {
      sidebar.classList.toggle('mobile-open');
    });

    // Global Search Input
    const globalSearch = document.getElementById('global-search-input');
    if (globalSearch) {
      globalSearch.addEventListener('input', () => renderGlobalSearchResults(globalSearch.value));
      globalSearch.addEventListener('focus', () => {
        if (globalSearch.value.trim()) renderGlobalSearchResults(globalSearch.value);
      });
      document.addEventListener('click', (event) => {
        const box = globalSearch.closest('.search-box');
        if (box && !box.contains(event.target)) {
          const results = document.getElementById('global-search-results');
          if (results) results.hidden = true;
        }
      });
    }

    // Players Filters
    document.getElementById('players-search-input')?.addEventListener('input', (e) => {
      state.playersFilter.query = e.target.value.toLowerCase().trim();
      renderPlayers();
    });

    document.getElementById('players-team-filter')?.addEventListener('change', (e) => {
      state.playersFilter.team = e.target.value;
      renderPlayers();
    });

    document.getElementById('players-position-filter')?.addEventListener('change', (e) => {
      state.playersFilter.position = e.target.value;
      renderPlayers();
    });

    // Matches Tab Filter Buttons
    document.querySelectorAll('.match-tab-btn').forEach(btn => {
      btn.addEventListener('click', (e) => {
        document.querySelectorAll('.match-tab-btn').forEach(b => b.classList.remove('active'));
        e.currentTarget.classList.add('active');
        state.matchFilter = e.currentTarget.dataset.matchFilter;
        renderMatches();
      });
    });

    // Modal Triggers
    document.getElementById('btn-open-add-team-modal')?.addEventListener('click', () => openModal('ADD_TEAM'));
    document.getElementById('teams-add-team-btn')?.addEventListener('click', () => openModal('ADD_TEAM'));
    document.getElementById('players-add-player-btn')?.addEventListener('click', () => openModal('ADD_PLAYER'));
    document.getElementById('coaches-add-coach-btn')?.addEventListener('click', () => openModal('ADD_COACH'));
    document.getElementById('btn-open-schedule-match-modal')?.addEventListener('click', () => openModal('SCHEDULE_MATCH'));
    document.getElementById('matches-schedule-btn')?.addEventListener('click', () => openModal('SCHEDULE_MATCH'));
    document.getElementById('venues-add-venue-btn')?.addEventListener('click', () => openModal('ADD_VENUE'));
    document.getElementById('referees-add-referee-btn')?.addEventListener('click', () => openModal('ADD_REFEREE'));
    document.getElementById('tournament-create-btn')?.addEventListener('click', () => openModal('CREATE_TOURNAMENT'));
    document.getElementById('quick-add-btn')?.addEventListener('click', () => openModal('ADD_TEAM'));

    // Close Modal Listener
    document.getElementById('modal-close-btn')?.addEventListener('click', closeModal);
    document.getElementById('modal-overlay')?.addEventListener('click', (e) => {
      if (e.target.id === 'modal-overlay') closeModal();
    });

    // Dashboard Quick Links
    document.getElementById('dash-view-all-matches')?.addEventListener('click', () => switchSubView('matches'));
    document.getElementById('dash-view-standings')?.addEventListener('click', () => switchSubView('standings'));

    // Footer Navigation Links
    document.getElementById('footer-link-dash')?.addEventListener('click', (e) => { e.preventDefault(); switchScreen('app'); switchSubView('dashboard'); });
    document.getElementById('footer-link-teams')?.addEventListener('click', (e) => { e.preventDefault(); switchScreen('app'); switchSubView('teams'); });
    document.getElementById('footer-link-fixtures')?.addEventListener('click', (e) => { e.preventDefault(); switchScreen('app'); switchSubView('matches'); });
    document.getElementById('footer-link-standings')?.addEventListener('click', (e) => { e.preventDefault(); switchScreen('app'); switchSubView('standings'); });

    // Standings Export CSV
    document.getElementById('standings-export-btn')?.addEventListener('click', () => exportStandingsCSV());

    // Reports Print
    document.getElementById('reports-print-btn')?.addEventListener('click', () => window.print());
  }

  function renderGlobalSearchResults(rawQuery) {
    const input = document.getElementById('global-search-input');
    if (!input) return;
    const box = input.closest('.search-box');
    if (!box) return;
    let panel = document.getElementById('global-search-results');
    if (!panel) {
      panel = document.createElement('div');
      panel.id = 'global-search-results';
      panel.className = 'global-search-results';
      panel.style.cssText = 'position:absolute;top:calc(100% + 8px);left:0;right:0;z-index:1200;max-height:340px;overflow:auto;background:var(--surface-card, #111827);border:1px solid var(--border-color, #374151);border-radius:10px;box-shadow:0 12px 28px rgba(0,0,0,.25);padding:6px;';
      box.style.position = 'relative';
      box.appendChild(panel);
    }
    const q = String(rawQuery || '').trim().toLowerCase();
    if (!q) {
      panel.hidden = true;
      return;
    }
    const items = [];
    state.teams.forEach(t => {
      if ([t.name, t.coach, t.city].some(v => String(v || '').toLowerCase().includes(q))) {
        items.push({type:'Team',label:t.name,detail:'Team / Franchise',view:'teams',id:t.id});
      }
    });
    state.players.forEach(p => {
      if ([p.name, p.position, p.teamName, p.jerseyNumber].some(v => String(v ?? '').toLowerCase().includes(q))) {
        items.push({type:'Player',label:p.name,detail:`${p.position} • ${p.teamName} • #${p.jerseyNumber}`,view:'players',id:p.id});
      }
    });
    state.matches.forEach(m => {
      if ([m.homeTeamName, m.awayTeamName, m.venue, m.date, m.status].some(v => String(v || '').toLowerCase().includes(q))) {
        items.push({type:'Match',label:`${m.homeTeamName} vs ${m.awayTeamName}`,detail:`${m.date} • ${m.status} • ${m.venue}`,view:'matches',id:m.id});
      }
    });
    state.venues.forEach(v => {
      if ([v.name, v.address].some(value => String(value || '').toLowerCase().includes(q))) {
        items.push({type:'Venue',label:v.name,detail:v.address || 'Venue / Stadium',view:'venues',id:v.id});
      }
    });
    (state.tournaments || []).forEach(t => {
      if ([t.name, t.format, t.status].some(value => String(value || '').toLowerCase().includes(q))) {
        items.push({type:'Tournament',label:t.name,detail:`${t.format} • ${t.status}`,view:'tournaments',id:t.id});
      }
    });
    panel.innerHTML = items.length ? items.slice(0, 12).map(item => `
      <button type="button" class="global-search-result" data-view="${item.view}" data-type="${item.type}" data-id="${escapeHtml(item.id)}" style="display:block;width:100%;text-align:left;border:0;border-radius:7px;padding:9px 10px;background:transparent;color:inherit;cursor:pointer;">
        <span style="display:block;font-weight:700;">${escapeHtml(item.label)}</span>
        <span style="display:block;font-size:.78rem;opacity:.72;">${escapeHtml(item.type)} · ${escapeHtml(item.detail)}</span>
      </button>
    `).join('') : '<div style="padding:12px;font-size:.9rem;opacity:.75;">No teams, players, matches, venues, or tournaments found.</div>';
    panel.hidden = false;
    panel.querySelectorAll('.global-search-result').forEach(button => {
      button.addEventListener('mouseenter', () => { button.style.background = 'rgba(148,163,184,.14)'; });
      button.addEventListener('mouseleave', () => { button.style.background = 'transparent'; });
      button.addEventListener('click', () => {
        const view = button.dataset.view;
        if (view === 'players') {
          state.playersFilter.query = q;
          const localSearch = document.getElementById('players-search-input');
          if (localSearch) localSearch.value = q;
        } else if (view === 'teams') {
          state.teamSearchQuery = q;
        } else if (view === 'matches') {
          state.matchSearchQuery = q;
        } else if (view === 'venues') {
          state.venueSearchQuery = q;
        }
        switchSubView(view);
        renderAllViews();
        panel.hidden = true;
      });
    });
  }

  function switchScreen(screenName) {
    state.activeScreen = screenName;
    document.querySelectorAll('.view-screen').forEach(s => s.classList.remove('active'));

    if (screenName === 'landing') {
      document.getElementById('landing-view').classList.add('active');
    } else if (screenName === 'login') {
      document.getElementById('login-view').classList.add('active');
    } else if (screenName === 'app') {
      document.getElementById('app-layout').classList.add('active');
      renderAllViews();
    }
  }

  function switchSubView(viewName) {
    state.activeSubView = viewName;
    document.querySelectorAll('.menu-item').forEach(m => {
      m.classList.toggle('active', m.dataset.view === viewName);
    });
    document.querySelectorAll('.dashboard-subview').forEach(sv => {
      sv.classList.remove('active');
    });

    const target = document.getElementById(`view-${viewName}`);
    if (target) {
      target.classList.add('active');
      // Trigger chart re-render if switching to dashboard or reports
      if (viewName === 'dashboard') {
        renderDashboardCharts();
      } else if (viewName === 'reports') {
        renderReportsCharts();
      }
    }
  }

  // Update Landing Page Counters
  function updateLandingStats() {
    const statTeams = document.getElementById('landing-stat-teams');
    const statPlayers = document.getElementById('landing-stat-players');
    const statMatches = document.getElementById('landing-stat-matches');
    
    if (statTeams) statTeams.textContent = state.teams.length;
    if (statPlayers) statPlayers.textContent = `${state.players.length}+`;
    if (statMatches) statMatches.textContent = state.matches.length;
  }

  function updateApiDocsLink() {
    const link = document.getElementById('api-docs-link');
    if (!link) return;
    if (window.__APEX_CONFIG__ && window.__APEX_CONFIG__.DOCS_URL) {
      link.href = window.__APEX_CONFIG__.DOCS_URL;
    } else if (API_BASE.startsWith('http')) {
      link.href = API_BASE.replace(/\/api\/?$/, '') + '/docs';
    } else if (API_BASE === '/api') {
      link.href = '/docs';
    }
  }

  // ==========================================
  // RENDER ALL VIEWS
  // ==========================================
  function renderAllViews() {
    renderDashboardKPIs();
    renderLeaderboardWidget();
    renderRecentMatchesTable();
    renderNextFixtureWidget();
    renderDashboardCharts();
    renderTeams();
    renderPlayers();
    renderCoaches();
    renderMatches();
    renderTournaments();
    renderVenues();
    renderReferees();
    renderStandings();
    renderReportsCharts();
    populatePlayerTeamDropdown();
  }

  // ------------------------------------------
  // 1. DASHBOARD SUB-VIEW
  // ------------------------------------------
  function renderDashboardKPIs() {
    document.getElementById('kpi-total-teams').textContent = state.teams.length;
    document.getElementById('kpi-registered-players').textContent = state.players.length;
    
    const upcoming = state.matches.filter(m => m.status === 'UPCOMING').length;
    const completed = state.matches.filter(m => m.status === 'COMPLETED').length;
    
    document.getElementById('kpi-upcoming-matches').textContent = upcoming;
    document.getElementById('kpi-completed-matches').textContent = completed;
    document.getElementById('kpi-active-tournaments').textContent = 3 + (state.tournaments || []).length;
    document.getElementById('kpi-total-coaches').textContent = state.coaches.length;
    document.getElementById('kpi-total-referees').textContent = state.referees.length;
  }

  function renderLeaderboardWidget() {
    const sorted = [...state.teams].sort((a, b) => b.points - a.points).slice(0, 5);
    const container = document.getElementById('dash-leaderboard-list');
    if (!container) return;

    container.innerHTML = sorted.map((team, idx) => `
      <div class="leaderboard-item">
        <div style="display: flex; align-items: center; gap: 0.65rem;">
          <span class="rank-badge rank-${idx + 1}">${idx + 1}</span>
          <img src="${team.logo}" alt="${team.name}" class="team-logo-sm">
          <span style="font-weight: 600; font-size: 0.9rem;">${team.name}</span>
        </div>
        <span style="font-weight: 800; color: var(--color-primary);">${team.points} pts</span>
      </div>
    `).join('');
  }

  function renderRecentMatchesTable() {
    const tbody = document.getElementById('dash-recent-matches-tbody');
    if (!tbody) return;

    tbody.innerHTML = state.matches.slice(0, 5).map(m => `
      <tr>
        <td style="color: var(--text-muted); font-size: 0.8rem;">${m.date}</td>
        <td>
          <div class="team-cell">
            <img src="${m.homeLogo}" class="team-logo-sm">
            <span>${m.homeTeamName}</span>
          </div>
        </td>
        <td style="font-weight: 800; font-size: 1rem; color: var(--color-cyan);">
          ${m.status === 'UPCOMING' ? 'VS' : `${m.homeScore} - ${m.awayScore}`}
        </td>
        <td>
          <div class="team-cell">
            <img src="${m.awayLogo}" class="team-logo-sm">
            <span>${m.awayTeamName}</span>
          </div>
        </td>
        <td style="color: var(--text-muted);">${m.venue}</td>
        <td>
          <span class="badge ${m.status === 'LIVE' ? 'badge-danger' : m.status === 'COMPLETED' ? 'badge-success' : 'badge-warning'}">
            ${m.status === 'LIVE' ? '<i class="fa-solid fa-signal"></i> LIVE' : m.status}
          </span>
        </td>
        <td>
          <button class="btn btn-sm btn-outline update-score-btn" data-id="${m.id}"><i class="fa-solid fa-pen"></i> Update</button>
        </td>
      </tr>
    `).join('');

    document.querySelectorAll('.update-score-btn').forEach(btn => {
      btn.addEventListener('click', () => openModal('UPDATE_SCORE', btn.dataset.id));
    });
  }

  function renderNextFixtureWidget() {
    const nextMatch = state.matches.find(m => m.status === 'UPCOMING') || state.matches[0];
    const container = document.getElementById('dash-next-fixture-box');
    if (!container || !nextMatch) return;

    container.innerHTML = `
      <div style="display: flex; align-items: center; justify-content: space-around; padding: 1rem 0;">
        <div style="text-align: center;">
          <img src="${nextMatch.homeLogo}" style="width: 48px; height: 48px;">
          <div style="font-weight: 700; font-size: 0.85rem; margin-top: 0.35rem;">${nextMatch.homeTeamName}</div>
        </div>
        <div style="font-weight: 800; font-size: 1.25rem; color: var(--color-amber);">VS</div>
        <div style="text-align: center;">
          <img src="${nextMatch.awayLogo}" style="width: 48px; height: 48px;">
          <div style="font-weight: 700; font-size: 0.85rem; margin-top: 0.35rem;">${nextMatch.awayTeamName}</div>
        </div>
      </div>
      <div style="border-top: 1px solid var(--border-color); padding-top: 0.65rem; text-align: center; font-size: 0.8rem; color: var(--text-muted);">
        <i class="fa-solid fa-clock"></i> ${nextMatch.date} @ ${nextMatch.time} • ${nextMatch.venue}
      </div>
    `;
  }

  function renderDashboardCharts() {
    if (typeof Chart === 'undefined') return;

    // Chart 1: Team Performance
    const ctx1 = document.getElementById('chart-team-performance');
    if (ctx1) {
      if (chartInstances.teamPerf) chartInstances.teamPerf.destroy();
      
      const labels = state.teams.slice(0, 6).map(t => t.name);
      const goalsFor = state.teams.slice(0, 6).map(t => t.goalsFor);
      const goalsAgainst = state.teams.slice(0, 6).map(t => t.goalsAgainst);

      chartInstances.teamPerf = new Chart(ctx1, {
        type: 'bar',
        data: {
          labels,
          datasets: [
            { label: 'Goals Scored', data: goalsFor, backgroundColor: '#3b82f6', borderRadius: 6 },
            { label: 'Goals Conceded', data: goalsAgainst, backgroundColor: '#ef4444', borderRadius: 6 }
          ]
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          plugins: { legend: { labels: { color: '#9ca3af' } } },
          scales: {
            x: { ticks: { color: '#9ca3af' }, grid: { color: 'rgba(255,255,255,0.05)' } },
            y: { ticks: { color: '#9ca3af' }, grid: { color: 'rgba(255,255,255,0.05)' } }
          }
        }
      });
    }

    // Chart 2: Tournament Progress Doughnut
    const ctx2 = document.getElementById('chart-tournament-progress');
    if (ctx2) {
      if (chartInstances.tourProg) chartInstances.tourProg.destroy();

      chartInstances.tourProg = new Chart(ctx2, {
        type: 'doughnut',
        data: {
          labels: ['Completed Games', 'Remaining Games', 'Live Games'],
          datasets: [{
            data: [42, 18, 2],
            backgroundColor: ['#10b981', '#3b82f6', '#ef4444'],
            borderWidth: 0
          }]
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          plugins: { legend: { position: 'bottom', labels: { color: '#9ca3af', font: { size: 10 } } } }
        }
      });
    }
  }

  // ------------------------------------------
  // 2. TEAMS SUB-VIEW
  // ------------------------------------------
  function renderTeams() {
    const container = document.getElementById('teams-grid-container');
    if (!container) return;

    container.innerHTML = state.teams.map(team => `
      <div class="team-card">
        <img src="${team.logo}" alt="${team.name}" class="team-card-logo">
        <h3 class="team-card-title">${team.name}</h3>
        <p class="team-card-coach"><i class="fa-solid fa-clipboard-user"></i> Coach: ${team.coach}</p>
        
        <div class="team-stats-row">
          <div class="t-stat">
            <span class="t-val text-green">${team.wins}</span>
            <span class="t-lbl">Wins</span>
          </div>
          <div class="t-stat">
            <span class="t-val text-rose">${team.losses}</span>
            <span class="t-lbl">Losses</span>
          </div>
          <div class="t-stat">
            <span class="t-val text-amber">${team.draws}</span>
            <span class="t-lbl">Draws</span>
          </div>
          <div class="t-stat">
            <span class="t-val text-blue">${team.points}</span>
            <span class="t-lbl">Points</span>
          </div>
        </div>

        <div class="team-card-actions">
          <button class="btn btn-sm btn-outline team-view-players-btn" data-teamid="${team.id}"><i class="fa-solid fa-users"></i> Roster</button>
          <button class="btn btn-sm btn-outline team-edit-btn" data-id="${team.id}"><i class="fa-solid fa-pen-to-square"></i> Edit</button>
          <button class="btn btn-sm btn-glass team-delete-btn" data-id="${team.id}" style="color: var(--color-rose);"><i class="fa-solid fa-trash"></i></button>
        </div>
      </div>
    `).join('');

    document.querySelectorAll('.team-view-players-btn').forEach(btn => {
      btn.addEventListener('click', () => {
        state.playersFilter.team = btn.dataset.teamid;
        document.getElementById('players-team-filter').value = btn.dataset.teamid;
        switchSubView('players');
      });
    });

    document.querySelectorAll('.team-edit-btn').forEach(btn => {
      btn.addEventListener('click', () => openModal('EDIT_TEAM', btn.dataset.id));
    });

    document.querySelectorAll('.team-delete-btn').forEach(btn => {
      btn.addEventListener('click', () => deleteTeam(btn.dataset.id));
    });
  }

  async function deleteTeam(id) {
    if (confirm("Are you sure you want to delete this team?")) {
      if (isBackendConnected) {
        try {
          await fetch(`${API_BASE}/teams/${id}`, { method: 'DELETE' });
        } catch (e) {
          console.warn('Backend team delete error:', e);
        }
      }
      state.teams = state.teams.filter(t => t.id !== id);
      renderAllViews();
    }
  }

  // ------------------------------------------
  // 3. PLAYERS SUB-VIEW
  // ------------------------------------------
  function populatePlayerTeamDropdown() {
    const select = document.getElementById('players-team-filter');
    if (!select) return;

    const options = ['<option value="ALL">All Teams</option>']
      .concat(state.teams.map(t => `<option value="${t.id}">${t.name}</option>`));
    select.innerHTML = options.join('');
  }

  function renderPlayers() {
    const tbody = document.getElementById('players-tbody');
    if (!tbody) return;

    let filtered = state.players.filter(p => {
      const matchTeam = state.playersFilter.team === 'ALL' || p.teamId === state.playersFilter.team;
      const matchPos = state.playersFilter.position === 'ALL' || p.position === state.playersFilter.position;
      const matchQuery = !state.playersFilter.query || 
        p.name.toLowerCase().includes(state.playersFilter.query) || 
        p.jerseyNumber.toString() === state.playersFilter.query;
      return matchTeam && matchPos && matchQuery;
    });

    tbody.innerHTML = filtered.map(p => `
      <tr>
        <td style="color: var(--text-dim); font-size: 0.8rem;">${p.id}</td>
        <td>
          <div class="player-cell">
            <img src="${p.photo}" class="player-avatar">
            <span style="font-weight: 600;">${p.name}</span>
          </div>
        </td>
        <td>${p.age}</td>
        <td><span class="badge badge-cyan">${p.position}</span></td>
        <td style="font-weight: 500;">${p.teamName}</td>
        <td style="font-weight: 800; color: var(--color-primary);">#${p.jerseyNumber}</td>
        <td style="font-weight: 700; color: var(--color-accent);">${p.goals}</td>
        <td>${p.assists}</td>
        <td>
          <span style="color: var(--color-amber); font-weight: 700;">${p.yellowCards}🟨</span> / 
          <span style="color: var(--color-rose); font-weight: 700;">${p.redCards}🟥</span>
        </td>
        <td>
          <button class="btn btn-sm btn-outline delete-player-btn" data-id="${p.id}" style="color: var(--color-rose);"><i class="fa-solid fa-trash"></i></button>
        </td>
      </tr>
    `).join('');

    document.querySelectorAll('.delete-player-btn').forEach(btn => {
      btn.addEventListener('click', async () => {
        if (confirm("Delete this player record?")) {
          const pId = btn.dataset.id;
          if (isBackendConnected) {
            try {
              await fetch(`${API_BASE}/players/${pId}`, { method: 'DELETE' });
            } catch (e) {
              console.warn('Backend player delete error:', e);
            }
          }
          state.players = state.players.filter(p => p.id !== pId);
          renderPlayers();
          renderDashboardKPIs();
        }
      });
    });
  }

  // ------------------------------------------
  // 4. COACHES SUB-VIEW
  // ------------------------------------------
  function renderCoaches() {
    const container = document.getElementById('coaches-grid-container');
    if (!container) return;

    container.innerHTML = state.coaches.map(c => `
      <div class="coach-card">
        <img src="${c.photo}" alt="${c.name}" class="coach-avatar">
        <h3 style="font-size: 1.15rem;">${c.name}</h3>
        <p style="color: var(--color-cyan); font-weight: 600; font-size: 0.875rem; margin-bottom: 0.5rem;">${c.teamName}</p>
        <div style="font-size: 0.8rem; color: var(--text-muted); display: flex; flex-direction: column; gap: 0.35rem;">
          <span><i class="fa-solid fa-briefcase"></i> Experience: ${c.experience}</span>
          <span><i class="fa-solid fa-globe"></i> Nationality: ${c.nationality}</span>
          <span><i class="fa-solid fa-envelope"></i> ${c.contact}</span>
        </div>
      </div>
    `).join('');
  }

  // ------------------------------------------
  // 5. MATCHES SUB-VIEW
  // ------------------------------------------
  function renderMatches() {
    const container = document.getElementById('matches-list-container');
    if (!container) return;

    let filtered = state.matches;
    if (state.matchFilter !== 'ALL') {
      filtered = state.matches.filter(m => m.status === state.matchFilter);
    }

    container.innerHTML = filtered.map(m => `
      <div class="match-card">
        <div class="match-card-header">
          <span><i class="fa-solid fa-calendar"></i> ${m.date} @ ${m.time}</span>
          <span class="badge ${m.status === 'LIVE' ? 'badge-danger' : m.status === 'COMPLETED' ? 'badge-success' : 'badge-warning'}">
            ${m.status}
          </span>
        </div>
        
        <div class="match-teams-row">
          <div class="match-team">
            <img src="${m.homeLogo}" style="width: 44px; height: 44px;">
            <span class="match-team-name">${m.homeTeamName}</span>
          </div>

          <div class="match-score-center">
            <div class="score-display">${m.status === 'UPCOMING' ? 'VS' : `${m.homeScore} : ${m.awayScore}`}</div>
          </div>

          <div class="match-team">
            <img src="${m.awayLogo}" style="width: 44px; height: 44px;">
            <span class="match-team-name">${m.awayTeamName}</span>
          </div>
        </div>

        <div class="match-card-footer">
          <span><i class="fa-solid fa-location-dot"></i> ${m.venue}</span>
          <span><i class="fa-solid fa-whistle"></i> Ref: ${m.referee}</span>
        </div>
      </div>
    `).join('');
  }

  // ------------------------------------------
  // 6. TOURNAMENTS SUB-VIEW
  // ------------------------------------------
  function escapeHtml(value) {
    return String(value ?? '').replace(/[&<>"']/g, (char) => ({
      '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;'
    })[char]);
  }

  function renderTournaments() {
    const tournamentSection = document.getElementById('view-tournaments');
    if (tournamentSection) {
      let createdList = document.getElementById('created-tournaments-list');
      if (!createdList) {
        createdList = document.createElement('div');
        createdList.id = 'created-tournaments-list';
        createdList.className = 'card mt-4';
        const heading = document.createElement('h3');
        heading.className = 'card-title';
        heading.textContent = 'Created Tournaments';
        createdList.appendChild(heading);
        const pageTitle = tournamentSection.querySelector('.page-title-row');
        if (pageTitle) pageTitle.insertAdjacentElement('afterend', createdList);
        else tournamentSection.prepend(createdList);
      }
      const query = (document.getElementById('global-search-input')?.value || '').trim().toLowerCase();
      const tournaments = state.tournaments.filter(t => !query || t.name.toLowerCase().includes(query) || t.format.toLowerCase().includes(query));
      createdList.innerHTML = '<h3 class="card-title">Created Tournaments</h3>' + (
        tournaments.length
          ? '<div class="grid-2-col mt-3">' + tournaments.map(t => `
              <article class="card">
                <div class="card-header">
                  <div>
                    <h4 class="card-title">${escapeHtml(t.name)}</h4>
                    <p class="card-subtitle">${escapeHtml(t.format)} • ${t.teamCount} teams</p>
                  </div>
                  <span class="badge badge-cyan">${escapeHtml(t.status)}</span>
                </div>
                <p class="card-subtitle">Starts: ${escapeHtml(t.startDate)}</p>
                <button type="button" class="btn btn-sm btn-outline tournament-delete-btn" data-id="${t.id}"><i class="fa-solid fa-trash"></i> Delete</button>
              </article>
            `).join('') + '</div>'
          : '<p class="card-subtitle mt-3">' + (query ? 'No created tournaments match your search.' : 'No tournaments created yet. Use “Create Tournament” to add one.') + '</p>'
      );
      createdList.querySelectorAll('.tournament-delete-btn').forEach(btn => {
        btn.addEventListener('click', () => {
          if (!confirm('Delete this tournament?')) return;
          state.tournaments = state.tournaments.filter(t => t.id !== btn.dataset.id);
          try { localStorage.setItem('apexLeagueTournaments', JSON.stringify(state.tournaments)); } catch (_) {}
          renderTournaments();
          renderDashboardKPIs();
        });
      });
    }

    // Render Knockout Bracket
    const bracketContainer = document.getElementById('knockout-bracket-container');
    if (bracketContainer) {
      const qf = state.bracket.quarterFinals;
      const sf = state.bracket.semiFinals;
      const final = state.bracket.final;

      bracketContainer.innerHTML = `
        <!-- Quarter Finals Column -->
        <div class="bracket-column">
          <div style="font-weight: 700; color: var(--text-muted); margin-bottom: 0.5rem; text-align: center;">Quarter-Finals</div>
          ${qf.map(m => `
            <div class="bracket-match">
              <div class="bracket-team-line ${m.winner === m.team1 ? 'winner' : ''}">
                <span>${m.team1}</span> <span>${m.score1}</span>
              </div>
              <div class="bracket-team-line ${m.winner === m.team2 ? 'winner' : ''}">
                <span>${m.team2}</span> <span>${m.score2}</span>
              </div>
            </div>
          `).join('')}
        </div>

        <!-- Semi Finals Column -->
        <div class="bracket-column">
          <div style="font-weight: 700; color: var(--text-muted); margin-bottom: 0.5rem; text-align: center;">Semi-Finals</div>
          ${sf.map(m => `
            <div class="bracket-match">
              <div class="bracket-team-line ${m.winner === m.team1 ? 'winner' : ''}">
                <span>${m.team1}</span> <span>${m.score1}</span>
              </div>
              <div class="bracket-team-line ${m.winner === m.team2 ? 'winner' : ''}">
                <span>${m.team2}</span> <span>${m.score2}</span>
              </div>
            </div>
          `).join('')}
        </div>

        <!-- Grand Final Column -->
        <div class="bracket-column">
          <div style="font-weight: 700; color: var(--color-amber); margin-bottom: 0.5rem; text-align: center;"><i class="fa-solid fa-trophy"></i> Grand Final</div>
          ${final.map(m => `
            <div class="bracket-match" style="border-color: var(--color-amber);">
              <div class="bracket-team-line">
                <span>${m.team1}</span> <span>${m.score1}</span>
              </div>
              <div class="bracket-team-line">
                <span>${m.team2}</span> <span>${m.score2}</span>
              </div>
            </div>
          `).join('')}
        </div>
      `;
    }

    // Group Stage Summary Table
    const groupTbody = document.getElementById('tournament-group-tbody');
    if (groupTbody) {
      groupTbody.innerHTML = state.teams.slice(0, 4).map(t => `
        <tr>
          <td style="font-weight: 600;">${t.name}</td>
          <td>3</td>
          <td class="text-green">${t.wins}</td>
          <td class="text-amber">${t.draws}</td>
          <td class="text-rose">${t.losses}</td>
          <td style="font-weight: 800; color: var(--color-primary);">${t.points}</td>
        </tr>
      `).join('');
    }
  }

  // ------------------------------------------
  // 7. VENUES & REFEREES SUB-VIEWS
  // ------------------------------------------
  function renderVenues() {
    const container = document.getElementById('venues-grid-container');
    if (!container) return;

    container.innerHTML = state.venues.map(v => `
      <div class="venue-card">
        <img src="${v.image}" class="venue-img">
        <div class="venue-details">
          <h3>${v.name}</h3>
          <p style="color: var(--text-muted); font-size: 0.85rem; margin-top: 0.25rem;"><i class="fa-solid fa-location-dot"></i> ${v.address}</p>
          <div style="display: flex; justify-content: space-between; margin-top: 1rem; font-size: 0.8rem;">
            <span><i class="fa-solid fa-chair"></i> Capacity: ${v.capacity}</span>
            <span class="badge badge-cyan">${v.upcomingMatchesCount} Scheduled</span>
          </div>
        </div>
      </div>
    `).join('');
  }

  function renderReferees() {
    const container = document.getElementById('referees-grid-container');
    if (!container) return;

    container.innerHTML = state.referees.map(r => `
      <div class="coach-card">
        <img src="${r.photo}" class="coach-avatar" style="border-color: var(--color-accent);">
        <h3>${r.name}</h3>
        <p style="color: var(--color-amber); font-weight: 700; margin: 0.25rem 0;"><i class="fa-solid fa-star"></i> ${r.rating} Rating</p>
        <p style="font-size: 0.8rem; color: var(--text-muted);">${r.experience}</p>
        <div style="margin-top: 0.75rem;">
          <span class="badge badge-outline"><i class="fa-solid fa-whistle"></i> ${r.assignedMatches} Matches Officiated</span>
        </div>
      </div>
    `).join('');
  }

  // ------------------------------------------
  // 8. STANDINGS SUB-VIEW
  // ------------------------------------------
  function renderStandings() {
    const tbody = document.getElementById('standings-tbody');
    if (!tbody) return;

    const sorted = [...state.teams].sort((a, b) => b.points - a.points || (b.goalsFor - b.goalsAgainst) - (a.goalsFor - a.goalsAgainst));

    tbody.innerHTML = sorted.map((t, idx) => {
      const rank = idx + 1;
      const mp = t.wins + t.losses + t.draws;
      const gd = t.goalsFor - t.goalsAgainst;

      let zoneClass = '';
      if (rank <= 4) zoneClass = 'zone-champions';
      else if (rank === 5) zoneClass = 'zone-europa';
      else if (rank >= 7) zoneClass = 'zone-relegation';

      return `
        <tr class="${zoneClass}">
          <td style="font-weight: 800;">${rank}</td>
          <td>
            <div class="team-cell">
              <img src="${t.logo}" class="team-logo-sm">
              <span>${t.name}</span>
            </div>
          </td>
          <td>${mp}</td>
          <td class="text-green" style="font-weight: 700;">${t.wins}</td>
          <td class="text-amber">${t.draws}</td>
          <td class="text-rose">${t.losses}</td>
          <td>${t.goalsFor}</td>
          <td>${t.goalsAgainst}</td>
          <td style="font-weight: 700;">${gd > 0 ? `+${gd}` : gd}</td>
          <td style="font-weight: 800; font-size: 1rem; color: var(--color-primary);">${t.points}</td>
          <td>
            <span style="font-size: 0.7rem;">🟩 🟩 🟧 🟩 🟥</span>
          </td>
        </tr>
      `;
    }).join('');
  }

  function exportStandingsCSV() {
    const sorted = [...state.teams].sort((a, b) => b.points - a.points || (b.goalsFor - b.goalsAgainst) - (a.goalsFor - a.goalsAgainst));
    const headers = ['Rank', 'Team', 'MP', 'W', 'D', 'L', 'GF', 'GA', 'GD', 'Points'];
    const rows = sorted.map((t, idx) => {
      const mp = t.wins + t.losses + t.draws;
      const gd = t.goalsFor - t.goalsAgainst;
      return [idx + 1, `"${t.name}"`, mp, t.wins, t.draws, t.losses, t.goalsFor, t.goalsAgainst, gd, t.points].join(',');
    });
    const csv = [headers.join(','), ...rows].join('\n');
    const blob = new Blob([csv], { type: 'text/csv' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = 'league_standings_2026.csv';
    a.click();
    URL.revokeObjectURL(url);
  }

  // ------------------------------------------
  // 9. REPORTS & ANALYTICS SUB-VIEW
  // ------------------------------------------
  function renderReportsCharts() {
    if (typeof Chart === 'undefined') return;

    // Chart 1: Goals per team
    const ctx1 = document.getElementById('chart-goals-per-team');
    if (ctx1) {
      if (chartInstances.goalsPerTeam) chartInstances.goalsPerTeam.destroy();

      chartInstances.goalsPerTeam = new Chart(ctx1, {
        type: 'bar',
        data: {
          labels: state.teams.map(t => t.name),
          datasets: [{
            label: 'Total Goals',
            data: state.teams.map(t => t.goalsFor),
            backgroundColor: '#10b981',
            borderRadius: 6
          }]
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          plugins: { legend: { labels: { color: '#9ca3af' } } },
          scales: {
            x: { ticks: { color: '#9ca3af' }, grid: { color: 'rgba(255,255,255,0.05)' } },
            y: { ticks: { color: '#9ca3af' }, grid: { color: 'rgba(255,255,255,0.05)' } }
          }
        }
      });
    }

    // Chart 2: Win Rate
    const ctx2 = document.getElementById('chart-win-rate');
    if (ctx2) {
      if (chartInstances.winRate) chartInstances.winRate.destroy();

      chartInstances.winRate = new Chart(ctx2, {
        type: 'pie',
        data: {
          labels: state.teams.slice(0, 5).map(t => t.name),
          datasets: [{
            data: state.teams.slice(0, 5).map(t => t.wins),
            backgroundColor: ['#3b82f6', '#10b981', '#f59e0b', '#06b6d4', '#8b5cf6']
          }]
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          plugins: { legend: { position: 'bottom', labels: { color: '#9ca3af' } } }
        }
      });
    }

    // Chart 3: Top Player Goals
    const ctx3 = document.getElementById('chart-player-goals');
    if (ctx3) {
      if (chartInstances.playerGoals) chartInstances.playerGoals.destroy();

      const topPlayers = [...state.players].sort((a, b) => b.goals - a.goals).slice(0, 6);

      chartInstances.playerGoals = new Chart(ctx3, {
        type: 'bar',
        data: {
          labels: topPlayers.map(p => p.name),
          datasets: [{
            label: 'Individual Goals',
            data: topPlayers.map(p => p.goals),
            backgroundColor: '#06b6d4',
            borderRadius: 6
          }]
        },
        options: {
          indexAxis: 'y',
          responsive: true,
          maintainAspectRatio: false,
          plugins: { legend: { labels: { color: '#9ca3af' } } },
          scales: {
            x: { ticks: { color: '#9ca3af' }, grid: { color: 'rgba(255,255,255,0.05)' } },
            y: { ticks: { color: '#9ca3af' }, grid: { color: 'rgba(255,255,255,0.05)' } }
          }
        }
      });
    }

    // Chart 4: Points Trend
    const ctx4 = document.getElementById('chart-points-trend');
    if (ctx4) {
      if (chartInstances.pointsTrend) chartInstances.pointsTrend.destroy();

      chartInstances.pointsTrend = new Chart(ctx4, {
        type: 'line',
        data: {
          labels: ['Week 1', 'Week 2', 'Week 3', 'Week 4', 'Week 5', 'Week 6'],
          datasets: [
            { label: 'Apex Strikers', data: [3, 6, 9, 12, 13, 16], borderColor: '#3b82f6', tension: 0.3 },
            { label: 'Titanium Titans', data: [3, 4, 7, 10, 13, 14], borderColor: '#10b981', tension: 0.3 }
          ]
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          plugins: { legend: { labels: { color: '#9ca3af' } } },
          scales: {
            x: { ticks: { color: '#9ca3af' }, grid: { color: 'rgba(255,255,255,0.05)' } },
            y: { ticks: { color: '#9ca3af' }, grid: { color: 'rgba(255,255,255,0.05)' } }
          }
        }
      });
    }
  }

  // ==========================================
  // DYNAMIC MODAL MANAGER
  // ==========================================
  function openModal(type, targetId = null) {
    const overlay = document.getElementById('modal-overlay');
    const title = document.getElementById('modal-title');
    const body = document.getElementById('modal-body');

    overlay.classList.add('active');

    if (type === 'ADD_TEAM') {
      title.textContent = 'Add New Franchised Team';
      body.innerHTML = `
        <form id="modal-form">
          <div class="form-group">
            <label>Team Name</label>
            <input type="text" class="form-control" id="f-team-name" required placeholder="e.g. Iron Clad FC">
          </div>
          <div class="form-group">
            <label>Head Coach Name</label>
            <input type="text" class="form-control" id="f-team-coach" required placeholder="e.g. Carlos Silva">
          </div>
          <div class="form-group">
            <label>City / Region</label>
            <input type="text" class="form-control" id="f-team-city" placeholder="e.g. Boston">
          </div>
          <button type="submit" class="btn btn-primary btn-block mt-3"><i class="fa-solid fa-plus"></i> Save Franchise</button>
        </form>
      `;

      document.getElementById('modal-form').onsubmit = async (e) => {
        e.preventDefault();
        const name = document.getElementById('f-team-name').value;
        const coach = document.getElementById('f-team-coach').value;
        const city = document.getElementById('f-team-city').value || 'City';

        const newTeam = {
          id: `T${state.teams.length + 1}`,
          name,
          logo: `https://api.dicebear.com/7.x/identicon/svg?seed=${encodeURIComponent(name)}`,
          coach,
          wins: 0,
          losses: 0,
          draws: 0,
          goalsFor: 0,
          goalsAgainst: 0,
          points: 0,
          city,
          founded: 2026
        };

        if (isBackendConnected) {
          try {
            const res = await fetch(`${API_BASE}/teams`, {
              method: 'POST',
              headers: { 'Content-Type': 'application/json' },
              body: JSON.stringify({ name, coach, city })
            });
            if (res.ok) {
              const serverTeam = await res.json();
              newTeam.id = serverTeam.id;
            }
          } catch (err) {
            console.warn('Backend team create error:', err);
          }
        }

        state.teams.push(newTeam);
        closeModal();
        renderAllViews();
      };
    } else if (type === 'EDIT_TEAM') {
      const team = state.teams.find(t => String(t.id) === String(targetId));
      if (!team) {
        closeModal();
        alert('Team not found.');
        return;
      }
      title.textContent = 'Edit Team Details';
      body.innerHTML = `
        <form id="modal-form">
          <div class="form-group">
            <label for="f-team-name">Team Name</label>
            <input type="text" class="form-control" id="f-team-name" required maxlength="100" value="${escapeHtml(team.name)}">
          </div>
          <div class="form-group">
            <label for="f-team-coach">Head Coach</label>
            <input type="text" class="form-control" id="f-team-coach" required maxlength="100" value="${escapeHtml(team.coach || '')}">
          </div>
          <div class="form-group">
            <label for="f-team-city">City / Region</label>
            <input type="text" class="form-control" id="f-team-city" maxlength="100" value="${escapeHtml(team.city || '')}">
          </div>
          <button type="submit" class="btn btn-primary btn-block mt-3"><i class="fa-solid fa-floppy-disk"></i> Save Changes</button>
        </form>
      `;
      document.getElementById('modal-form').onsubmit = async (e) => {
        e.preventDefault();
        const name = document.getElementById('f-team-name').value.trim();
        const coach = document.getElementById('f-team-coach').value.trim();
        const city = document.getElementById('f-team-city').value.trim() || 'City';
        if (!name || !coach) {
          alert('Team name and coach are required.');
          return;
        }
        if (state.teams.some(t => String(t.id) !== String(team.id) && t.name.toLowerCase() === name.toLowerCase())) {
          alert('A team with that name already exists.');
          return;
        }
        if (isBackendConnected) {
          try {
            const res = await fetch(`${API_BASE}/teams/${encodeURIComponent(team.id)}`, {
              method: 'PUT',
              headers: { 'Content-Type': 'application/json' },
              body: JSON.stringify({ name, coach, city })
            });
            if (!res.ok) throw new Error('The server could not update this team.');
          } catch (err) {
            alert(err.message || 'Could not update team on the server. Please try again.');
            return;
          }
        }
        team.name = name;
        team.coach = coach;
        team.city = city;
        state.players.forEach(p => {
          if (String(p.teamId) === String(team.id)) p.teamName = name;
        });
        state.matches.forEach(m => {
          if (String(m.homeTeamId) === String(team.id)) m.homeTeamName = name;
          if (String(m.awayTeamId) === String(team.id)) m.awayTeamName = name;
        });
        closeModal();
        renderAllViews();
      };
    } else if (type === 'ADD_PLAYER') {
      title.textContent = 'Register New Player';
      body.innerHTML = `
        <form id="modal-form">
          <div class="form-group">
            <label>Full Name</label>
            <input type="text" class="form-control" id="f-player-name" required placeholder="e.g. Jordan Henderson">
          </div>
          <div class="form-group">
            <label>Position</label>
            <select class="form-control" id="f-player-pos">
              <option value="Forward">Forward</option>
              <option value="Midfielder">Midfielder</option>
              <option value="Defender">Defender</option>
              <option value="Goalkeeper">Goalkeeper</option>
            </select>
          </div>
          <div class="form-group">
            <label>Team</label>
            <select class="form-control" id="f-player-team">
              ${state.teams.map(t => `<option value="${t.id}">${t.name}</option>`).join('')}
            </select>
          </div>
          <div class="form-group">
            <label>Jersey Number</label>
            <input type="number" class="form-control" id="f-player-jersey" value="10" required>
          </div>
          <button type="submit" class="btn btn-primary btn-block mt-3"><i class="fa-solid fa-user-plus"></i> Complete Registration</button>
        </form>
      `;

      document.getElementById('modal-form').onsubmit = async (e) => {
        e.preventDefault();
        const name = document.getElementById('f-player-name').value;
        const position = document.getElementById('f-player-pos').value;
        const teamId = document.getElementById('f-player-team').value;
        const team = state.teams.find(t => t.id === teamId);
        const jerseyNumber = parseInt(document.getElementById('f-player-jersey').value, 10);

        if (!name.trim()) {
          alert('Please enter the player name.');
          return;
        }
        if (!team) {
          alert('Please create a team before registering a player.');
          return;
        }
        if (!Number.isInteger(jerseyNumber) || jerseyNumber < 0 || jerseyNumber > 99) {
          alert('Jersey number must be a whole number between 0 and 99.');
          return;
        }
        if (state.players.some(p => String(p.teamId) === String(teamId) && Number(p.jerseyNumber) === jerseyNumber)) {
          alert('That jersey number is already assigned to a player in this team.');
          return;
        }

        const newPlayer = {
          id: `P${state.players.length + 101}`,
          name,
          age: 24,
          position,
          teamId,
          teamName: team ? team.name : 'Unassigned',
          jerseyNumber,
          goals: 0,
          assists: 0,
          yellowCards: 0,
          redCards: 0,
          photo: "https://images.unsplash.com/photo-1500648767791-00dcc994a43e?auto=format&fit=crop&w=150&q=80"
        };

        if (isBackendConnected) {
          try {
            const res = await fetch(`${API_BASE}/players`, {
              method: 'POST',
              headers: { 'Content-Type': 'application/json' },
              body: JSON.stringify({
                name,
                position,
                team_id: teamId,
                jersey_number: jerseyNumber
              })
            });
            if (res.ok) {
              const serverPlayer = await res.json();
              newPlayer.id = serverPlayer.id;
            }
          } catch (err) {
            console.warn('Backend player create error:', err);
          }
        }

        state.players.push(newPlayer);
        closeModal();
        renderAllViews();
      };
    } else if (type === 'CREATE_TOURNAMENT') {
      title.textContent = 'Create Tournament';
      body.innerHTML = `
        <form id="modal-form">
          <div class="form-group">
            <label for="f-tournament-name">Tournament Name</label>
            <input type="text" class="form-control" id="f-tournament-name" required maxlength="100" placeholder="e.g. Apex Champions Cup">
          </div>
          <div class="form-group">
            <label for="f-tournament-format">Format</label>
            <select class="form-control" id="f-tournament-format" required>
              <option value="Knockout">Knockout</option>
              <option value="League">League</option>
              <option value="Group Stage + Knockout">Group Stage + Knockout</option>
            </select>
          </div>
          <div class="form-group">
            <label for="f-tournament-start">Start Date</label>
            <input type="date" class="form-control" id="f-tournament-start" required>
          </div>
          <div class="form-group">
            <label for="f-tournament-teams">Number of Teams</label>
            <input type="number" class="form-control" id="f-tournament-teams" min="2" max="64" value="8" required>
          </div>
          <button type="submit" class="btn btn-primary btn-block mt-3"><i class="fa-solid fa-trophy"></i> Create Tournament</button>
        </form>
      `;

      document.getElementById('modal-form').onsubmit = (e) => {
        e.preventDefault();
        const name = document.getElementById('f-tournament-name').value.trim();
        const format = document.getElementById('f-tournament-format').value;
        const startDate = document.getElementById('f-tournament-start').value;
        const teamCount = Number(document.getElementById('f-tournament-teams').value);
        if (!name || !startDate || !Number.isInteger(teamCount) || teamCount < 2 || teamCount > 64) {
          alert('Please enter a tournament name, start date, and a team count between 2 and 64.');
          return;
        }
        const tournament = {
          id: 'TOUR-' + Date.now(),
          name,
          format,
          startDate,
          teamCount,
          status: 'Planned',
          createdAt: new Date().toISOString()
        };
        state.tournaments.unshift(tournament);
        try { localStorage.setItem('apexLeagueTournaments', JSON.stringify(state.tournaments)); } catch (err) {
          console.warn('Could not save tournaments in this browser:', err);
        }
        closeModal();
        renderTournaments();
        renderDashboardKPIs();
      };
    } else if (type === 'SCHEDULE_MATCH') {
      title.textContent = 'Schedule League Match';
      body.innerHTML = `
        <form id="modal-form">
          <div class="form-group">
            <label>Home Team</label>
            <select class="form-control" id="f-home-team">
              ${state.teams.map(t => `<option value="${t.id}">${t.name}</option>`).join('')}
            </select>
          </div>
          <div class="form-group">
            <label>Away Team</label>
            <select class="form-control" id="f-away-team">
              ${state.teams.map((t, idx) => `<option value="${t.id}" ${idx === 1 ? 'selected' : ''}>${t.name}</option>`).join('')}
            </select>
          </div>
          <div class="form-group">
            <label>Date & Time</label>
            <input type="text" class="form-control" id="f-match-date" value="2026-08-10 19:00 EST">
          </div>
          <div class="form-group">
            <label>Venue</label>
            <select class="form-control" id="f-match-venue">
              ${state.venues.map(v => `<option value="${v.name}">${v.name}</option>`).join('')}
            </select>
          </div>
          <button type="submit" class="btn btn-primary btn-block mt-3"><i class="fa-solid fa-calendar-check"></i> Save Fixture</button>
        </form>
      `;

      document.getElementById('modal-form').onsubmit = async (e) => {
        e.preventDefault();
        const hId = document.getElementById('f-home-team').value;
        const aId = document.getElementById('f-away-team').value;
        const hTeam = state.teams.find(t => t.id === hId);
        const aTeam = state.teams.find(t => t.id === aId);
        const rawDate = document.getElementById('f-match-date').value;
        const venue = document.getElementById('f-match-venue').value;

        const newMatch = {
          id: `M${state.matches.length + 101}`,
          homeTeamId: hId,
          homeTeamName: hTeam ? hTeam.name : 'Home Team',
          homeLogo: hTeam ? hTeam.logo : '',
          awayTeamId: aId,
          awayTeamName: aTeam ? aTeam.name : 'Away Team',
          awayLogo: aTeam ? aTeam.logo : '',
          date: rawDate.split(' ')[0],
          time: rawDate.split(' ')[1] || '19:00 EST',
          venue,
          referee: "Michael Oliver",
          status: "UPCOMING",
          homeScore: 0,
          awayScore: 0
        };

        if (isBackendConnected) {
          try {
            const res = await fetch(`${API_BASE}/matches`, {
              method: 'POST',
              headers: { 'Content-Type': 'application/json' },
              body: JSON.stringify({
                home_team_id: hId,
                away_team_id: aId,
                date: newMatch.date,
                time: newMatch.time,
                venue
              })
            });
            if (res.ok) {
              const serverMatch = await res.json();
              newMatch.id = serverMatch.id;
            }
          } catch (err) {
            console.warn('Backend match schedule error:', err);
          }
        }

        state.matches.unshift(newMatch);
        closeModal();
        renderAllViews();
      };
    } else if (type === 'UPDATE_SCORE') {
      const match = state.matches.find(m => m.id === targetId);
      if (!match) return;

      title.textContent = `Update Result: ${match.homeTeamName} vs ${match.awayTeamName}`;
      body.innerHTML = `
        <form id="modal-form">
          <div class="grid-2-col">
            <div class="form-group">
              <label>${match.homeTeamName} Score</label>
              <input type="number" class="form-control" id="f-score-home" value="${match.homeScore}">
            </div>
            <div class="form-group">
              <label>${match.awayTeamName} Score</label>
              <input type="number" class="form-control" id="f-score-away" value="${match.awayScore}">
            </div>
          </div>
          <div class="form-group">
            <label>Status</label>
            <select class="form-control" id="f-match-status">
              <option value="LIVE" ${match.status === 'LIVE' ? 'selected' : ''}>LIVE</option>
              <option value="COMPLETED" ${match.status === 'COMPLETED' ? 'selected' : ''}>COMPLETED</option>
              <option value="UPCOMING" ${match.status === 'UPCOMING' ? 'selected' : ''}>UPCOMING</option>
            </select>
          </div>
          <button type="submit" class="btn btn-primary btn-block mt-3"><i class="fa-solid fa-floppy-disk"></i> Submit Score</button>
        </form>
      `;

      document.getElementById('modal-form').onsubmit = async (e) => {
        e.preventDefault();
        const hScore = parseInt(document.getElementById('f-score-home').value);
        const aScore = parseInt(document.getElementById('f-score-away').value);
        const mStatus = document.getElementById('f-match-status').value;

        if (isBackendConnected) {
          try {
            await fetch(`${API_BASE}/matches/${match.id}/score`, {
              method: 'PUT',
              headers: { 'Content-Type': 'application/json' },
              body: JSON.stringify({
                home_score: hScore,
                away_score: aScore,
                status: mStatus
              })
            });
            await fetchAllFromBackend();
          } catch (err) {
            console.warn('Backend match score error:', err);
          }
        }

        match.homeScore = hScore;
        match.awayScore = aScore;
        match.status = mStatus;

        closeModal();
        renderAllViews();
      };
    } else {
      title.textContent = 'Action Dialog';
      body.innerHTML = '<p>Operation successfully executed.</p>';
    }
  }

  function closeModal() {
    document.getElementById('modal-overlay')?.classList.remove('active');
  }

  // ==========================================
  // BACKEND API SYNCHRONIZATION
  // ==========================================
  async function checkAndSyncBackend() {
    const pill = document.getElementById('backend-status-pill');
    const text = document.getElementById('backend-status-text');
    try {
      const res = await fetch(`${API_BASE}/health`, { signal: AbortSignal.timeout(2500) });
      if (res.ok) {
        isBackendConnected = true;
        if (pill) {
          pill.className = 'backend-status-pill online';
          if (text) text.innerHTML = '<i class="fa-solid fa-circle-check"></i> API Connected';
          pill.title = `Live connected to Apex REST Backend (${API_BASE})`;
        }
        await fetchAllFromBackend();
        renderAllViews();
        return;
      }
    } catch (err) {
      // Offline fallback
    }

    isBackendConnected = false;
    if (pill) {
      pill.className = 'backend-status-pill offline';
      if (text) text.innerHTML = '<i class="fa-solid fa-database"></i> Standalone Mode';
      pill.title = `Running in Standalone Mode (${API_BASE} unavailable)`;
    }
  }

  async function fetchAllFromBackend() {
    try {
      const [tRes, pRes, mRes, cRes, vRes, rRes, bRes] = await Promise.all([
        fetch(`${API_BASE}/teams`),
        fetch(`${API_BASE}/players`),
        fetch(`${API_BASE}/matches`),
        fetch(`${API_BASE}/coaches`),
        fetch(`${API_BASE}/venues`),
        fetch(`${API_BASE}/referees`),
        fetch(`${API_BASE}/tournaments/bracket`)
      ]);

      if (tRes.ok) {
        const rawTeams = await tRes.json();
        state.teams = rawTeams.map(t => ({
          id: t.id,
          name: t.name,
          logo: t.logo,
          coach: t.coach,
          wins: t.wins,
          losses: t.losses,
          draws: t.draws,
          goalsFor: t.goals_for,
          goalsAgainst: t.goals_against,
          points: t.points,
          city: t.city,
          founded: t.founded
        }));
      }

      if (pRes.ok) {
        const rawPlayers = await pRes.json();
        state.players = rawPlayers.map(p => ({
          id: p.id,
          name: p.name,
          age: p.age,
          position: p.position,
          teamId: p.team_id,
          teamName: p.team_name,
          jerseyNumber: p.jersey_number,
          goals: p.goals,
          assists: p.assists,
          yellowCards: p.yellow_cards,
          redCards: p.red_cards,
          photo: p.photo
        }));
      }

      if (mRes.ok) {
        const rawMatches = await mRes.json();
        state.matches = rawMatches.map(m => ({
          id: m.id,
          homeTeamId: m.home_team_id,
          homeTeamName: m.home_team_name,
          homeLogo: m.home_logo,
          awayTeamId: m.away_team_id,
          awayTeamName: m.away_team_name,
          awayLogo: m.away_logo,
          date: m.date,
          time: m.time,
          venue: m.venue,
          referee: m.referee,
          status: m.status,
          homeScore: m.home_score,
          awayScore: m.away_score
        }));
      }

      if (cRes.ok) {
        const rawCoaches = await cRes.json();
        state.coaches = rawCoaches.map(c => ({
          id: c.id,
          name: c.name,
          teamName: c.team_name,
          experience: c.experience,
          nationality: c.nationality,
          contact: c.contact,
          photo: c.photo
        }));
      }

      if (vRes.ok) {
        const rawVenues = await vRes.json();
        state.venues = rawVenues.map(v => ({
          id: v.id,
          name: v.name,
          image: v.image,
          capacity: v.capacity,
          address: v.address,
          upcomingMatchesCount: v.upcoming_matches_count
        }));
      }

      if (rRes.ok) {
        const rawReferees = await rRes.json();
        state.referees = rawReferees.map(r => ({
          id: r.id,
          name: r.name,
          experience: r.experience,
          assignedMatches: r.assigned_matches,
          rating: r.rating,
          photo: r.photo
        }));
      }

      if (bRes.ok) {
        state.bracket = await bRes.json();
      }
    } catch (err) {
      console.warn('Backend sync fetch error:', err);
    }
  }

})();
