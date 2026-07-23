import { useState, useEffect } from 'react';
import apiClient from '../api/client';

export default function DiscoveryBoard() {
    const [upcomingFlights, setUpcomingFlights] = useState([]);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        // Fetch the 3-month rolling window from the Django backend
        apiClient.get('flights/upcoming/')
            .then(response => {
                setUpcomingFlights(response.data);
                setLoading(false);
            })
            .catch(error => {
                console.error("Error fetching flights:", error);
                setLoading(false);
            });
    }, []);

    if (loading) {
        return (
            <div className="flex justify-center items-center py-12">
                <p className="text-gray-500 font-medium">Loading upcoming routes...</p>
            </div>
        );
    }

    if (upcomingFlights.length === 0) {
        return null; // Hide the board if the database is completely empty
    }

    return (
        <div className="mt-8">
            <h2 className="text-2xl font-bold text-gray-800 mb-6 px-2">
                Explore Upcoming Destinations
            </h2>
            
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                {upcomingFlights.map(flight => (
                    <div 
                        key={flight.id} 
                        className="bg-white p-6 rounded-2xl shadow-sm border-t-4 border-pastelBlue hover:shadow-md transition-shadow"
                    >
                        <div className="flex justify-between items-center mb-4">
                            <span className="font-bold text-gray-800 truncate">{flight.airline}</span>
                            <span className="text-sm font-bold text-julianna bg-creame px-3 py-1 rounded-full">
                                ₹{flight.price}
                            </span>
                        </div>
                        
                        <div className="flex justify-between items-center text-gray-700 mb-4 font-medium">
                            <span className="truncate">{flight.source}</span>
                            <span className="text-gray-400 px-2">✈️</span>
                            <span className="truncate">{flight.destination}</span>
                        </div>
                        
                        <div className="text-sm text-gray-500 mt-4 border-t border-gray-100 pt-4 flex justify-between">
                            <span>{new Date(flight.departure_time).toLocaleDateString(undefined, { month: 'short', day: 'numeric' })}</span>
                            <span>{new Date(flight.departure_time).toLocaleTimeString(undefined, { hour: '2-digit', minute: '2-digit' })}</span>
                        </div>
                    </div>
                ))}
            </div>
        </div>
    );
}