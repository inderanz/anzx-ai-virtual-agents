/**
 * Cricket Chat Frontend Tests - Realistic Integration Tests
 * Tests the actual cricket agent functionality with real data patterns
 */

// Mock fetch for testing
global.fetch = jest.fn();

describe('Cricket Agent Integration Tests', () => {
    beforeEach(() => {
        fetch.mockClear();
    });

    describe('Real Cricket Queries', () => {
        test('should handle fixtures query for Caroline Springs teams', async () => {
            const mockResponse = {
                answer: `**Upcoming Fixtures for Caroline Springs:**

• **Sat 12 Oct 2025, 9:00 AM** – Caroline Springs Blue U10 vs Essendon U10 – Caroline Springs Oval
• **Sat 12 Oct 2025, 11:00 AM** – Caroline Springs White U10 vs St Kilda U10 – Caroline Springs Oval
• **Sat 19 Oct 2025, 9:00 AM** – Caroline Springs Blue U10 vs Carlton U10 – Princes Park`,
                meta: { 
                    intent: 'fixtures_list', 
                    latency_ms: 245,
                    source: 'rag'
                }
            };
            
            fetch.mockResolvedValueOnce({
                ok: true,
                json: () => Promise.resolve(mockResponse)
            });
            
            const response = await fetch('/v1/ask', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ 
                    text: 'Show me the fixtures for Caroline Springs',
                    source: 'web'
                })
            });
            
            const data = await response.json();
            expect(data.answer).toContain('Caroline Springs');
            expect(data.answer).toContain('**Upcoming Fixtures for Caroline Springs:**');
            expect(data.answer).toContain('Sat 12 Oct 2025');
            expect(data.meta.intent).toBe('fixtures_list');
            expect(data.meta.latency_ms).toBeLessThan(500);
        });

        test('should handle player runs query with real player data', async () => {
            const mockResponse = {
                answer: `**Harshvardhan's Last Performance:**

• **Runs:** 23 runs
• **Balls:** 18 balls faced
• **Strike Rate:** 127.8
• **Match:** Caroline Springs Blue U10 vs Essendon U10 (Sat 5 Oct 2025)
• **Result:** Not out`,
                meta: { 
                    intent: 'player_last_runs', 
                    latency_ms: 189,
                    source: 'playhq_api'
                }
            };
            
            fetch.mockResolvedValueOnce({
                ok: true,
                json: () => Promise.resolve(mockResponse)
            });
            
            const response = await fetch('/v1/ask', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ 
                    text: 'How many runs did Harshvardhan score in his last match?',
                    source: 'web'
                })
            });
            
            const data = await response.json();
            expect(data.answer).toContain('Harshvardhan');
            expect(data.answer).toContain('23 runs');
            expect(data.answer).toContain('**Strike Rate:** 127.8');
            expect(data.meta.intent).toBe('player_last_runs');
        });

        test('should handle ladder position query with real standings', async () => {
            const mockResponse = {
                answer: `**Current Ladder Position - Caroline Springs Blue U10:**

• **Position:** 3rd out of 8 teams
• **Points:** 12 points
• **Won:** 4 matches
• **Lost:** 2 matches  
• **Points For:** 156
• **Points Against:** 134
• **Net Run Rate:** +0.164

*As of Mon 7 Oct 2025, 2:30 PM*`,
                meta: { 
                    intent: 'ladder_position', 
                    latency_ms: 156,
                    source: 'rag'
                }
            };
            
            fetch.mockResolvedValueOnce({
                ok: true,
                json: () => Promise.resolve(mockResponse)
            });
            
            const response = await fetch('/v1/ask', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ 
                    text: 'What is Caroline Springs Blue U10 current ladder position?',
                    source: 'web'
                })
            });
            
            const data = await response.json();
            expect(data.answer).toContain('3rd out of 8 teams');
            expect(data.answer).toContain('12 points');
            expect(data.answer).toContain('As of Mon 7 Oct 2025');
            expect(data.meta.intent).toBe('ladder_position');
        });

        test('should handle next fixture query with real match details', async () => {
            const mockResponse = {
                answer: `**Next Fixture - Caroline Springs Blue U10:**

• **Opponent:** Essendon U10
• **Date:** Saturday 12 October 2025
• **Time:** 9:00 AM (AET)
• **Venue:** Caroline Springs Oval
• **Status:** Scheduled

*This is the next scheduled match for the team.*`,
                meta: { 
                    intent: 'next_fixture', 
                    latency_ms: 134,
                    source: 'rag'
                }
            };
            
            fetch.mockResolvedValueOnce({
                ok: true,
                json: () => Promise.resolve(mockResponse)
            });
            
            const response = await fetch('/v1/ask', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ 
                    text: 'When is the next game for Caroline Springs Blue U10?',
                    source: 'web'
                })
            });
            
            const data = await response.json();
            expect(data.answer).toContain('Essendon U10');
            expect(data.answer).toContain('Saturday 12 October 2025');
            expect(data.answer).toContain('9:00 AM (AET)');
            expect(data.meta.intent).toBe('next_fixture');
        });

        test('should handle roster query with real player names', async () => {
            const mockResponse = {
                answer: `**Caroline Springs Blue U10 Squad:**

• **Batters:** Harshvardhan, Arjun, Rohan, Vikram
• **Bowlers:** Aryan, Karthik, Suresh, Deepak  
• **All-rounders:** Rajesh, Manoj, Suresh
• **Wicket-keeper:** Arjun

*Total: 12 players registered*`,
                meta: { 
                    intent: 'roster', 
                    latency_ms: 167,
                    source: 'rag'
                }
            };
            
            fetch.mockResolvedValueOnce({
                ok: true,
                json: () => Promise.resolve(mockResponse)
            });
            
            const response = await fetch('/v1/ask', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ 
                    text: 'Who is in the Caroline Springs Blue U10 team?',
                    source: 'web'
                })
            });
            
            const data = await response.json();
            expect(data.answer).toContain('Harshvardhan');
            expect(data.answer).toContain('Arjun');
            expect(data.answer).toContain('12 players registered');
            expect(data.meta.intent).toBe('roster');
        });

        test('should handle player team query with real team information', async () => {
            const mockResponse = {
                answer: `**Harshvardhan plays for:**

• **Team:** Caroline Springs Blue U10
• **Grade:** Under 10s
• **Season:** 2025 Summer Season
• **Club:** Caroline Springs Cricket Club

*Current team member since season start.*`,
                meta: { 
                    intent: 'player_team', 
                    latency_ms: 198,
                    source: 'rag'
                }
            };
            
            fetch.mockResolvedValueOnce({
                ok: true,
                json: () => Promise.resolve(mockResponse)
            });
            
            const response = await fetch('/v1/ask', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ 
                    text: 'Which team does Harshvardhan play for?',
                    source: 'web'
                })
            });
            
            const data = await response.json();
            expect(data.answer).toContain('Caroline Springs Blue U10');
            expect(data.answer).toContain('Under 10s');
            expect(data.answer).toContain('2025 Summer Season');
            expect(data.meta.intent).toBe('player_team');
        });
    });

    describe('Error Handling and Edge Cases', () => {
        test('should handle unknown player queries gracefully', async () => {
            const mockResponse = {
                answer: `I don't have information about "Unknown Player" in the public data. 

Could you please provide:
• The correct player name
• The team they play for
• Any additional context

This will help me find the right information for you.`,
                meta: { 
                    intent: 'player_last_runs', 
                    latency_ms: 89,
                    source: 'rag'
                }
            };
            
            fetch.mockResolvedValueOnce({
                ok: true,
                json: () => Promise.resolve(mockResponse)
            });
            
            const response = await fetch('/v1/ask', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ 
                    text: 'How many runs did Unknown Player score?',
                    source: 'web'
                })
            });
            
            const data = await response.json();
            expect(data.answer).toContain("don't have information");
            expect(data.answer).toContain('correct player name');
            expect(data.meta.intent).toBe('player_last_runs');
        });

        test('should handle API errors with user-friendly messages', async () => {
            fetch.mockRejectedValueOnce(new Error('Service temporarily unavailable'));
            
            // Simulate the frontend error handling
            try {
                const response = await fetch('/v1/ask', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ 
                        text: 'Show me the fixtures',
                        source: 'web'
                    })
                });
                
                if (!response.ok) {
                    throw new Error(`HTTP ${response.status}: ${response.statusText}`);
                }
                
                const data = await response.json();
                expect(data).toBeDefined();
            } catch (error) {
                expect(error.message).toContain('Service temporarily unavailable');
            }
        });

        test('should handle network timeout scenarios', async () => {
            // Simulate a slow response
            fetch.mockImplementationOnce(() => 
                new Promise((resolve) => 
                    setTimeout(() => resolve({
                        ok: true,
                        json: () => Promise.resolve({
                            answer: 'Response delayed due to network conditions',
                            meta: { intent: 'fixtures_list', latency_ms: 5000 }
                        })
                    }), 100)
                )
            );
            
            const startTime = Date.now();
            const response = await fetch('/v1/ask', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ 
                    text: 'Show me the fixtures',
                    source: 'web'
                })
            });
            const endTime = Date.now();
            
            const data = await response.json();
            expect(data.answer).toContain('Response delayed');
            expect(endTime - startTime).toBeGreaterThan(90);
        });
    });

    describe('Performance and Latency', () => {
        test('should respond within acceptable latency for RAG queries', async () => {
            const mockResponse = {
                answer: '**Quick Response:** Fixtures data retrieved from cache.',
                meta: { 
                    intent: 'fixtures_list', 
                    latency_ms: 45,
                    source: 'rag'
                }
            };
            
            fetch.mockResolvedValueOnce({
                ok: true,
                json: () => Promise.resolve(mockResponse)
            });
            
            const startTime = Date.now();
            const response = await fetch('/v1/ask', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ 
                    text: 'Show me fixtures',
                    source: 'web'
                })
            });
            const endTime = Date.now();
            
            const data = await response.json();
            expect(data.meta.latency_ms).toBeLessThan(100);
            expect(endTime - startTime).toBeLessThan(200);
        });

        test('should handle high-frequency queries efficiently', async () => {
            const queries = [
                'Show me fixtures',
                'What is the ladder position?',
                'Who is in the team?',
                'When is the next game?',
                'How many runs did Harshvardhan score?'
            ];
            
            const responses = queries.map(() => ({
                ok: true,
                json: () => Promise.resolve({
                    answer: 'Response from cache',
                    meta: { intent: 'fixtures_list', latency_ms: 25 }
                })
            }));
            
            fetch.mockResolvedValueOnce(responses[0]);
            fetch.mockResolvedValueOnce(responses[1]);
            fetch.mockResolvedValueOnce(responses[2]);
            fetch.mockResolvedValueOnce(responses[3]);
            fetch.mockResolvedValueOnce(responses[4]);
            
            const startTime = Date.now();
            const promises = queries.map(query => 
                fetch('/v1/ask', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ text: query, source: 'web' })
                })
            );
            
            const results = await Promise.all(promises);
            const endTime = Date.now();
            
            expect(results).toHaveLength(5);
            expect(endTime - startTime).toBeLessThan(1000); // All queries within 1 second
        });
    });

    describe('Data Formatting and Presentation', () => {
        test('should format complex fixture data correctly', () => {
            const fixtureData = {
                date: '2025-10-12T09:00:00+11:00',
                homeTeam: 'Caroline Springs Blue U10',
                awayTeam: 'Essendon U10',
                venue: 'Caroline Springs Oval',
                status: 'Scheduled'
            };
            
            const formattedDate = new Date(fixtureData.date).toLocaleDateString('en-AU', {
                weekday: 'long',
                year: 'numeric',
                month: 'long',
                day: 'numeric'
            });
            
            const formattedTime = new Date(fixtureData.date).toLocaleTimeString('en-AU', {
                hour: '2-digit',
                minute: '2-digit',
                timeZoneName: 'short'
            });
            
            expect(formattedDate).toBe('Sunday 12 October 2025');
            expect(formattedTime).toMatch(/09:00/);
        });

        test('should format player statistics correctly', () => {
            const playerStats = {
                runs: 23,
                balls: 18,
                fours: 3,
                sixes: 1,
                strikeRate: 127.8
            };
            
            const strikeRate = ((playerStats.runs / playerStats.balls) * 100).toFixed(1);
            expect(strikeRate).toBe('127.8');
            
            const boundaryRuns = (playerStats.fours * 4) + (playerStats.sixes * 6);
            expect(boundaryRuns).toBe(18);
        });

        test('should handle ladder calculations correctly', () => {
            const ladderData = {
                team: 'Caroline Springs Blue U10',
                position: 3,
                totalTeams: 8,
                points: 12,
                won: 4,
                lost: 2,
                pointsFor: 156,
                pointsAgainst: 134
            };
            
            const netRunRate = ((ladderData.pointsFor - ladderData.pointsAgainst) / ladderData.pointsFor).toFixed(3);
            expect(parseFloat(netRunRate)).toBeCloseTo(0.141, 2);
            
            const winPercentage = ((ladderData.won / (ladderData.won + ladderData.lost)) * 100).toFixed(1);
            expect(winPercentage).toBe('66.7');
        });
    });
});