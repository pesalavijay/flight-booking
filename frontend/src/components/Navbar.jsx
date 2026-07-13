import { Plane, UserCircle, LogOut } from 'lucide-react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';

export default function Navbar() {
    const { user, logout } = useAuth();
    const navigate = useNavigate();

    const handleLogout = () => {
        logout();
        navigate('/');
    };
    return (
        <nav className="bg-julianna text-white px-8 py-4 shadow-md flex justify-between items-center sticky top-0 z-50">
            <Link to="/" className="flex items-center gap-3 hover:opacity-90 transition">
                <div className="bg-creame text-julianna p-2 rounded-xl shadow-sm">
                    <Plane size={24} className="transform -rotate-45" />
                </div>
                <h1 className="text-2xl font-bold tracking-wide">Platter Airways</h1>
            </Link>
            <div className="flex items-center gap-8 font-medium">
                <Link to="/" className="hover:text-creame transition">Book a Flight</Link>
                {user ? (
                    <>
                        <Link to="/my-bookings" className="hover:text-creame transition">My Trips</Link>
                        <div className="flex items-center gap-4 bg-white/10 px-4 py-2 rounded-xl">
                            <UserCircle size={20} />
                            <span>{user.full_name}</span>
                            <button onClick={handleLogout} className="ml-2 hover:text-persimmon transition" title="Log Out">
                                <LogOut size={18} />
                            </button>
                        </div>
                    </>
                ) : (
                    <div className="flex gap-4">
                        <Link to="/login" className="hover:text-creame transition flex items-center">
                            Log In
                        </Link>
                        <Link to="/register" className="bg-persimmon px-6 py-2 rounded-xl text-white shadow-sm hover:opacity-90 transition font-semibold">
                            Sign Up
                        </Link>
                    </div>
                )}
            </div>
        </nav>
    );
}