import { useState, useEffect } from 'react';
import apiClient from '../api/client';

export default function Dashboard() {
    const [tickets, setTickets] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState('');

    useEffect(() => {
        // apiClient should automatically attach the user's JWT token in the headers
        apiClient.get('dashboard/tickets/')
            .then(response => {
                setTickets(response.data);
                setLoading(false);
            })
            .catch(err => {
                setError('Failed to load your dashboard. Please log in again.');
                setLoading(false);
            });
    }, []);

    if (loading) return <div className="text-center py-12 text-gray-500 font-medium">Loading your trips...</div>;
    if (error) return <div className="text-center py-12 text-red-500 font-medium">{error}</div>;

    return (
        <div className="min-h-screen bg-creame px-6 py-12">
            <div className="max-w-4xl mx-auto">
                <h1 className="text-3xl font-bold text-gray-900 mb-8">My Upcoming Trips</h1>
                
                {tickets.length === 0 ? (
                    <div className="bg-white p-8 rounded-2xl shadow-sm text-center">
                        <p className="text-gray-500">You have no upcoming flights.</p>
                    </div>
                ) : (
                    <div className="space-y-6">
                        {tickets.map(ticket => (
                            <div key={ticket.id} className="bg-white p-6 rounded-2xl shadow-sm border-l-4 border-pastelBlue flex justify-between items-center">
                                <div>
                                    <h3 className="text-xl font-bold text-gray-800">Booking ID: {ticket.booking_reference}</h3>
                                    <p className="text-gray-600 mt-1">{ticket.flight.source} → {ticket.flight.destination}</p>
                                    <p className="text-sm font-medium text-gray-500 mt-2">Status: <span className="text-green-600">{ticket.status}</span></p>
                                </div>
                                
                                <button className="bg-red-50 text-red-600 border border-red-200 px-6 py-2 rounded-lg font-semibold hover:bg-red-100 transition-colors">
                                    Cancel Ticket
                                </button>
                            </div>
                        ))}
                    </div>
                )}
            </div>
        </div>
    );
}