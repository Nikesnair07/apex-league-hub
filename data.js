// Initial Mock Data Store for Apex League Hub (Static Standalone Version)

window.ApexData = {
  initialTeams: [
    {
      id: "T1",
      name: "Apex Strikers FC",
      logo: "https://api.dicebear.com/7.x/identicon/svg?seed=ApexStrikers",
      coach: "Julian Alvarez",
      wins: 14,
      losses: 2,
      draws: 3,
      goalsFor: 42,
      goalsAgainst: 16,
      points: 45,
      city: "New York",
      founded: 2012
    },
    {
      id: "T2",
      name: "Titanium Titans",
      logo: "https://api.dicebear.com/7.x/identicon/svg?seed=TitaniumTitans",
      coach: "Marcus Vance",
      wins: 13,
      losses: 3,
      draws: 3,
      goalsFor: 38,
      goalsAgainst: 18,
      points: 42,
      city: "Chicago",
      founded: 2010
    },
    {
      id: "T3",
      name: "Vanguard Warriors",
      logo: "https://api.dicebear.com/7.x/identicon/svg?seed=VanguardWarriors",
      coach: "Elena Rostova",
      wins: 11,
      losses: 4,
      draws: 4,
      goalsFor: 34,
      goalsAgainst: 20,
      points: 37,
      city: "Los Angeles",
      founded: 2015
    },
    {
      id: "T4",
      name: "Solaris Dragons",
      logo: "https://api.dicebear.com/7.x/identicon/svg?seed=SolarisDragons",
      coach: "Diego Mendoza",
      wins: 10,
      losses: 5,
      draws: 4,
      goalsFor: 31,
      goalsAgainst: 22,
      points: 34,
      city: "Miami",
      founded: 2014
    },
    {
      id: "T5",
      name: "Cyber Pulse FC",
      logo: "https://api.dicebear.com/7.x/identicon/svg?seed=CyberPulse",
      coach: "Liam O'Connor",
      wins: 9,
      losses: 7,
      draws: 3,
      goalsFor: 29,
      goalsAgainst: 27,
      points: 30,
      city: "Seattle",
      founded: 2018
    },
    {
      id: "T6",
      name: "Phoenix Rising",
      logo: "https://api.dicebear.com/7.x/identicon/svg?seed=PhoenixRising",
      coach: "Sophia Chen",
      wins: 8,
      losses: 8,
      draws: 3,
      goalsFor: 27,
      goalsAgainst: 30,
      points: 27,
      city: "Phoenix",
      founded: 2017
    },
    {
      id: "T7",
      name: "Thunderbolt SC",
      logo: "https://api.dicebear.com/7.x/identicon/svg?seed=ThunderboltSC",
      coach: "Gabriel Silva",
      wins: 7,
      losses: 9,
      draws: 3,
      goalsFor: 24,
      goalsAgainst: 32,
      points: 24,
      city: "Dallas",
      founded: 2016
    },
    {
      id: "T8",
      name: "Neon Shadows",
      logo: "https://api.dicebear.com/7.x/identicon/svg?seed=NeonShadows",
      coach: "Kaito Tanaka",
      wins: 5,
      losses: 11,
      draws: 3,
      goalsFor: 20,
      goalsAgainst: 36,
      points: 18,
      city: "San Francisco",
      founded: 2019
    }
  ],

  initialPlayers: [
    { id: "P101", name: "Lucas Sterling", age: 26, position: "Forward", teamId: "T1", teamName: "Apex Strikers FC", jerseyNumber: 9, goals: 18, assists: 7, yellowCards: 2, redCards: 0, photo: "https://images.unsplash.com/photo-1500648767791-00dcc994a43e?auto=format&fit=crop&w=150&q=80" },
    { id: "P102", name: "Mateo Kovac", age: 24, position: "Midfielder", teamId: "T1", teamName: "Apex Strikers FC", jerseyNumber: 10, goals: 9, assists: 14, yellowCards: 3, redCards: 0, photo: "https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?auto=format&fit=crop&w=150&q=80" },
    { id: "P103", name: "Viktor Petrov", age: 29, position: "Defender", teamId: "T1", teamName: "Apex Strikers FC", jerseyNumber: 4, goals: 3, assists: 2, yellowCards: 5, redCards: 1, photo: "https://images.unsplash.com/photo-1492562080023-ab3db95bfbce?auto=format&fit=crop&w=150&q=80" },
    { id: "P104", name: "Gabriel Jesus", age: 27, position: "Forward", teamId: "T2", teamName: "Titanium Titans", jerseyNumber: 11, goals: 15, assists: 5, yellowCards: 1, redCards: 0, photo: "https://images.unsplash.com/photo-1506794778202-cad84cf45f1d?auto=format&fit=crop&w=150&q=80" },
    { id: "P105", name: "David Alaba", age: 31, position: "Defender", teamId: "T2", teamName: "Titanium Titans", jerseyNumber: 3, goals: 2, assists: 6, yellowCards: 4, redCards: 0, photo: "https://images.unsplash.com/photo-1519085360753-af0119f7cbe7?auto=format&fit=crop&w=150&q=80" },
    { id: "P106", name: "Antoine Griezmann", age: 28, position: "Midfielder", teamId: "T3", teamName: "Vanguard Warriors", jerseyNumber: 7, goals: 12, assists: 11, yellowCards: 2, redCards: 0, photo: "https://images.unsplash.com/photo-1522075469751-3a6694fb2f61?auto=format&fit=crop&w=150&q=80" },
    { id: "P107", name: "Manuel Neuer", age: 33, position: "Goalkeeper", teamId: "T1", teamName: "Apex Strikers FC", jerseyNumber: 1, goals: 0, assists: 1, yellowCards: 1, redCards: 0, photo: "https://images.unsplash.com/photo-1539571696357-5a69c17a67c6?auto=format&fit=crop&w=150&q=80" },
    { id: "P108", name: "Rodri Hernandez", age: 25, position: "Midfielder", teamId: "T4", teamName: "Solaris Dragons", jerseyNumber: 16, goals: 8, assists: 9, yellowCards: 6, redCards: 0, photo: "https://images.unsplash.com/photo-1517841905240-472988babdf9?auto=format&fit=crop&w=150&q=80" },
    { id: "P109", name: "Achraf Hakimi", age: 23, position: "Defender", teamId: "T5", teamName: "Cyber Pulse FC", jerseyNumber: 2, goals: 4, assists: 8, yellowCards: 3, redCards: 0, photo: "https://images.unsplash.com/photo-1501196354995-cbb51c65aaea?auto=format&fit=crop&w=150&q=80" },
    { id: "P110", name: "Son Heung-min", age: 30, position: "Forward", teamId: "T6", teamName: "Phoenix Rising", jerseyNumber: 7, goals: 14, assists: 6, yellowCards: 1, redCards: 0, photo: "https://images.unsplash.com/photo-1534528741775-53994a69daeb?auto=format&fit=crop&w=150&q=80" }
  ],

  initialCoaches: [
    { id: "C1", name: "Julian Alvarez", teamName: "Apex Strikers FC", experience: "12 Years", nationality: "Argentina", contact: "julian@apexstrikers.com", photo: "https://images.unsplash.com/photo-1560250097-0b93528c311a?auto=format&fit=crop&w=150&q=80" },
    { id: "C2", name: "Marcus Vance", teamName: "Titanium Titans", experience: "15 Years", nationality: "United States", contact: "vance@titansfc.com", photo: "https://images.unsplash.com/photo-1472099645785-5658abf4ff4e?auto=format&fit=crop&w=150&q=80" },
    { id: "C3", name: "Elena Rostova", teamName: "Vanguard Warriors", experience: "9 Years", nationality: "Spain", contact: "elena@vanguardw.com", photo: "https://images.unsplash.com/photo-1573496359142-b8d87734a5a2?auto=format&fit=crop&w=150&q=80" },
    { id: "C4", name: "Diego Mendoza", teamName: "Solaris Dragons", experience: "11 Years", nationality: "Brazil", contact: "diego@solaris.com", photo: "https://images.unsplash.com/photo-1519085360753-af0119f7cbe7?auto=format&fit=crop&w=150&q=80" }
  ],

  initialMatches: [
    {
      id: "M101",
      homeTeamId: "T1",
      homeTeamName: "Apex Strikers FC",
      homeLogo: "https://api.dicebear.com/7.x/identicon/svg?seed=ApexStrikers",
      awayTeamId: "T2",
      awayTeamName: "Titanium Titans",
      awayLogo: "https://api.dicebear.com/7.x/identicon/svg?seed=TitaniumTitans",
      date: "2026-08-01",
      time: "20:00 EST",
      venue: "Metropolitan Grand Arena",
      referee: "Michael Oliver",
      status: "LIVE",
      homeScore: 2,
      awayScore: 1
    },
    {
      id: "M102",
      homeTeamId: "T3",
      homeTeamName: "Vanguard Warriors",
      homeLogo: "https://api.dicebear.com/7.x/identicon/svg?seed=VanguardWarriors",
      awayTeamId: "T4",
      awayTeamName: "Solaris Dragons",
      awayLogo: "https://api.dicebear.com/7.x/identicon/svg?seed=SolarisDragons",
      date: "2026-08-03",
      time: "18:30 EST",
      venue: "Pacific Olympic Stadium",
      referee: "Szymon Marciniak",
      status: "UPCOMING",
      homeScore: 0,
      awayScore: 0
    },
    {
      id: "M103",
      homeTeamId: "T5",
      homeTeamName: "Cyber Pulse FC",
      homeLogo: "https://api.dicebear.com/7.x/identicon/svg?seed=CyberPulse",
      awayTeamId: "T6",
      awayTeamName: "Phoenix Rising",
      awayLogo: "https://api.dicebear.com/7.x/identicon/svg?seed=PhoenixRising",
      date: "2026-07-29",
      time: "19:00 EST",
      venue: "Emerald Tech Arena",
      referee: "Anthony Taylor",
      status: "COMPLETED",
      homeScore: 3,
      awayScore: 1
    },
    {
      id: "M104",
      homeTeamId: "T7",
      homeTeamName: "Thunderbolt SC",
      homeLogo: "https://api.dicebear.com/7.x/identicon/svg?seed=ThunderboltSC",
      awayTeamId: "T8",
      awayTeamName: "Neon Shadows",
      awayLogo: "https://api.dicebear.com/7.x/identicon/svg?seed=NeonShadows",
      date: "2026-07-28",
      time: "21:00 EST",
      venue: "Lone Star Coliseum",
      referee: "Clement Turpin",
      status: "COMPLETED",
      homeScore: 2,
      awayScore: 0
    }
  ],

  initialVenues: [
    {
      id: "V1",
      name: "Metropolitan Grand Arena",
      image: "https://images.unsplash.com/photo-1522778119026-d647f0596c20?auto=format&fit=crop&w=600&q=80",
      capacity: "65,000 Seats",
      address: "100 Championship Blvd, New York, NY",
      upcomingMatchesCount: 4
    },
    {
      id: "V2",
      name: "Pacific Olympic Stadium",
      image: "https://images.unsplash.com/photo-1577223625816-7546f13df25d?auto=format&fit=crop&w=600&q=80",
      capacity: "54,200 Seats",
      address: "777 Victory Drive, Los Angeles, CA",
      upcomingMatchesCount: 3
    },
    {
      id: "V3",
      name: "Emerald Tech Arena",
      image: "https://images.unsplash.com/photo-1574629810360-7efbbe195018?auto=format&fit=crop&w=600&q=80",
      capacity: "42,000 Seats",
      address: "500 Innovation Way, Seattle, WA",
      upcomingMatchesCount: 2
    }
  ],

  initialReferees: [
    { id: "R1", name: "Michael Oliver", experience: "14 Years FIFA Certified", assignedMatches: 18, rating: 4.9, photo: "https://images.unsplash.com/photo-1500648767791-00dcc994a43e?auto=format&fit=crop&w=150&q=80" },
    { id: "R2", name: "Szymon Marciniak", experience: "16 Years World Cup Ref", assignedMatches: 22, rating: 4.95, photo: "https://images.unsplash.com/photo-1472099645785-5658abf4ff4e?auto=format&fit=crop&w=150&q=80" },
    { id: "R3", name: "Anthony Taylor", experience: "11 Years Premier Panel", assignedMatches: 15, rating: 4.8, photo: "https://images.unsplash.com/photo-1519085360753-af0119f7cbe7?auto=format&fit=crop&w=150&q=80" },
    { id: "R4", name: "Clement Turpin", experience: "13 Years UEFA Elite", assignedMatches: 16, rating: 4.85, photo: "https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?auto=format&fit=crop&w=150&q=80" }
  ],

  initialBracketData: {
    quarterFinals: [
      { match: "QF1", team1: "Apex Strikers", score1: 3, team2: "Neon Shadows", score2: 0, winner: "Apex Strikers" },
      { match: "QF2", team1: "Titanium Titans", score1: 2, team2: "Thunderbolt SC", score2: 1, winner: "Titanium Titans" },
      { match: "QF3", team1: "Vanguard Warriors", score1: 4, team2: "Phoenix Rising", score2: 2, winner: "Vanguard Warriors" },
      { match: "QF4", team1: "Solaris Dragons", score1: 1, team2: "Cyber Pulse FC", score2: 0, winner: "Solaris Dragons" }
    ],
    semiFinals: [
      { match: "SF1", team1: "Apex Strikers", score1: 2, team2: "Titanium Titans", score2: 1, winner: "Apex Strikers" },
      { match: "SF2", team1: "Vanguard Warriors", score1: 1, team2: "Solaris Dragons", score2: 0, winner: "Vanguard Warriors" }
    ],
    final: [
      { match: "FINAL", team1: "Apex Strikers", score1: "-", team2: "Vanguard Warriors", score2: "-", winner: "TBD" }
    ]
  }
};
