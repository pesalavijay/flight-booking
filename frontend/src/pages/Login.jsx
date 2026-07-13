import { useState } from 'react';
import { useNavigate, Link, useLocation } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { Plane } from 'lucide-react';

export default function Login() {
    const navigate = useNavigate();
    const location = useLocation();
    const { login } = useAuth();
    const [formData, setFormData] = useState({ email: '', password: '' });
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState('');
    const from = location.state ?.from ?.pathname || "/";

    const handleLogin = async (e) => {
        e.preventDefault();
        setLoading(true);
        setError('');
        try {
            await login(formData.email, formData.password);
            navigate(from, { replace: true });
        } catch (err) {
            setError('Invalid email or password.');
        } finally {
            setLoading(false);
        }
    };
    return (
        <div className="min-h-[calc(100vh-80px)] bg-creame flex items-center justify-center p-6">
            <div className="bg-white p-10 rounded-3xl shadow-xl w-full max-w-md border-t-8 border-julianna">
                <div className="flex justify-center mb-6">
                    <div className="bg-pastelBlue p-3 rounded-2xl text-julianna">
                        <Plane size={32} className="transform -rotate-45" />
                    </div>
                </div>
                <h2 className="text-3xl font-bold text-center text-gray-900 mb-8">Welcome Back</h2>
                {error && <div className="bg-red-50 text-red-500 p-3 rounded-lg mb-6 text-sm text-center">{error}</div>}
                <form onSubmit={handleLogin} className="space-y-5">
                    <input type="email" required placeholder="Email Address" className="w-full p-4 border border-gray-200 rounded-xl outline-none focus:border-julianna focus:ring-1 focus:ring-julianna bg-gray-50"
                        onChange={(e) => setFormData({...formData, email: e.target.value})}
                    />
                    <input type="password" required placeholder="Password" className="w-full p-4 border border-gray-200 rounded-xl outline-none focus:border-julianna focus:ring-1 focus:ring-julianna bg-gray-50"
                        onChange={(e) => setFormData({...formData, password: e.target.value})}
                    />
                    <button type="submit" disabled={loading} className="w-full bg-julianna text-white font-bold py-4 rounded-xl hover:bg-opacity-90 transition-all shadow-md mt-2 disabled:opacity-50">
                        {loading ? 'Logging in...' : 'Log In'}
                    </button>
                </form>
                <p className="text-center text-gray-500 mt-6">
                    New to Platter Airways ? <Link to="/register" className="text-persimmon font-bold hover:underline">Create an account</Link>
                </p>
            </div>
        </div>
    );
}