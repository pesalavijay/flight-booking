import { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import apiClient from '../api/client';
import { Plane } from 'lucide-react';

export default function Register() {
    const navigate = useNavigate();
    const [formData, setFormData] = useState({ email: '', full_name: '', phone: '', password: '' });
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState('');
    const handleRegister = async (e) => {
        e.preventDefault();
        setLoading(true);
        setError('');
        try {
            await apiClient.post('users/register/', formData);
            alert('Account created successfully! Please log in.');
            navigate('/login');
        } catch (err) {
            setError(err.response?.data?.email?.[0] || 'Registration failed. Please check your details.');
        } finally {
            setLoading(false);
        }
    };
    return (
        <div className="min-h-[calc(100vh-80px)] bg-creame flex items-center justify-center p-6">
            <div className="bg-white p-10 rounded-3xl shadow-xl w-full max-w-md border-t-8 border-persimmon">
                <div className="flex justify-center mb-6">
                    <div className="bg-pastelBlue p-3 rounded-2xl text-julianna">
                        <Plane size={32} className="transform -rotate-45" />
                    </div>
                </div>
                <h2 className="text-3xl font-bold text-center text-gray-900 mb-8"> Join Platter Airways </h2>
                
                {error && <div className="bg-red-50 text-red-500 p-3 rounded-lg mb-6 text-sm text-center">{error}</div>}

                <form onSubmit={handleRegister} className="space-y-5">
                    <input type="text" required placeholder="Full Name"
                        className="w-full p-4 border border-gray-200 rounded-xl outline-none focus:border-julianna focus:ring-1 focus:ring-julianna bg-gray-50"
                        onChange={(e) => setFormData({...formData, full_name: e.target.value})}
                    />
                    <input type="email" required placeholder="Email Address"
                        className="w-full p-4 border border-gray-200 rounded-xl outline-none focus:border-julianna focus:ring-1 focus:ring-julianna bg-gray-50"
                        onChange={(e) => setFormData({...formData, email: e.target.value})}
                    />
                    <input type="tel" placeholder="Phone Number (Optional)"
                        className="w-full p-4 border border-gray-200 rounded-xl outline-none focus:border-julianna focus:ring-1 focus:ring-julianna bg-gray-50"
                        onChange={(e) => setFormData({...formData, phone: e.target.value})}
                    />
                    <input type="password" required placeholder="Create Password" minLength="6"
                        className="w-full p-4 border border-gray-200 rounded-xl outline-none focus:border-julianna focus:ring-1 focus:ring-julianna bg-gray-50"
                        onChange={(e) => setFormData({...formData, password: e.target.value})}
                    />
                    <button type="submit" disabled={loading}
                        className="w-full bg-persimmon text-white font-bold py-4 rounded-xl hover:bg-opacity-90 transition-all shadow-md mt-2 disabled:opacity-50">
                        {loading ? 'Creating Account...' : 'Sign Up'}
                    </button>
                </form>
                <p className="text-center text-gray-500 mt-6">
                    Already have an account? <Link to="/login" className="text-julianna font-bold hover:underline">Log in</Link>
                </p>
            </div>
        </div>
    );
}