import { useState } from 'react';
import { Lock, User, ArrowRight, Loader2 } from 'lucide-react';
import { apiUrl } from '@/lib/api'

interface LoginProps {
    onLogin: (token: string) => void;
}

export const Login = ({ onLogin }: LoginProps) => {
    const [isRegistering, setIsRegistering] = useState(false);
    const [username, setUsername] = useState('');
    const [password, setPassword] = useState('');
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState('');

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        setLoading(true);
        setError('');

        try {
            if (isRegistering) {
                // Register
                const res = await fetch(apiUrl('/auth/register'), {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ username, password })
                });
                if (!res.ok) throw new Error((await res.json()).detail || 'Registration failed');
                
                // Auto login after register? Or just switch to login
                setIsRegistering(false);
                setError('Account created! Please login.');
                setLoading(false);
            } else {
                // Login
                const formData = new FormData();
                formData.append('username', username);
                formData.append('password', password);

                const res = await fetch(apiUrl('/auth/token'), {
                    method: 'POST',
                    body: formData
                });
                if (!res.ok) throw new Error('Invalid credentials');
                
                const data = await res.json();
                onLogin(data.access_token);
            }
        } catch (err: any) {
            setError(err.message);
            setLoading(false);
        }
    };

    return (
        <div className="flex items-center justify-center min-h-screen bg-background text-foreground relative overflow-hidden">
            {/* Background Gradient */}
            <div className="absolute top-[-20%] left-[-10%] w-[50%] h-[50%] bg-primary/20 rounded-full blur-[120px] animate-pulse" />
            <div className="absolute bottom-[-20%] right-[-10%] w-[50%] h-[50%] bg-violet-900/20 rounded-full blur-[120px]" />

            <div className="relative z-10 w-full max-w-md p-8 bg-card border border-border rounded-2xl shadow-2xl animate-in">
                <div className="text-center mb-8">
                    <div className="w-12 h-12 bg-primary/10 rounded-xl mx-auto flex items-center justify-center border border-primary/20 mb-4 shadow-[0_0_15px_-3px_rgba(139,92,246,0.3)]">
                        <Lock className="w-5 h-5 text-primary" />
                    </div>
                    <h1 className="text-2xl font-bold tracking-tight text-foreground">Welcome to AION</h1>
                    <p className="text-muted-foreground mt-2 text-sm">Secure Ecosystem Orchestration</p>
                </div>

                <form onSubmit={handleSubmit} className="space-y-4">
                    <div className="space-y-2">
                        <label className="text-xs font-semibold text-muted-foreground uppercase tracking-wider">Username</label>
                        <div className="relative">
                            <User className="absolute left-3 top-2.5 w-4 h-4 text-muted-foreground" />
                            <input 
                                type="text"
                                required
                                value={username}
                                onChange={(e) => setUsername(e.target.value)}
                                className="w-full bg-secondary/50 border border-input rounded-lg py-2 pl-10 pr-4 text-sm focus:outline-none focus:border-primary focus:ring-1 focus:ring-primary transition-all placeholder:text-muted-foreground/50 text-foreground"
                                placeholder="Enter your identity"
                            />
                        </div>
                    </div>

                    <div className="space-y-2">
                        <label className="text-xs font-semibold text-muted-foreground uppercase tracking-wider">Password</label>
                        <div className="relative">
                            <Lock className="absolute left-3 top-2.5 w-4 h-4 text-muted-foreground" />
                            <input 
                                type="password"
                                required
                                value={password}
                                onChange={(e) => setPassword(e.target.value)}
                                className="w-full bg-secondary/50 border border-input rounded-lg py-2 pl-10 pr-4 text-sm focus:outline-none focus:border-primary focus:ring-1 focus:ring-primary transition-all placeholder:text-muted-foreground/50 text-foreground"
                                placeholder="••••••••"
                            />
                        </div>
                    </div>

                    {error && (
                        <div className={`text-xs p-2 rounded ${error.includes('created') ? 'bg-green-500/10 text-green-400' : 'bg-destructive/10 text-destructive'} text-center font-medium`}>
                            {error}
                        </div>
                    )}

                    <button 
                        type="submit" 
                        disabled={loading}
                        className="w-full bg-primary text-primary-foreground hover:bg-primary/90 font-bold py-2.5 rounded-lg shadow-lg flex items-center justify-center gap-2 transition-all disabled:opacity-50 disabled:cursor-not-allowed mt-6"
                    >
                        {loading ? <Loader2 className="w-4 h-4 animate-spin" /> : (
                            <>
                                {isRegistering ? 'Create Account' : 'Sign In'}
                                <ArrowRight className="w-4 h-4" />
                            </>
                        )}
                    </button>
                </form>

                <div className="mt-6 text-center">
                    <button 
                        onClick={() => { setIsRegistering(!isRegistering); setError(''); }}
                        className="text-xs text-muted-foreground hover:text-foreground transition-colors font-medium"
                    >
                        {isRegistering ? 'Already have an account? Sign in' : "Don't have an account? Register"}
                    </button>
                </div>
            </div>
        </div>
    );
};
