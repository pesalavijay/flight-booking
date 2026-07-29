import { useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import apiClient from '../api/client';
import { useAuth } from '../context/AuthContext';
import { Plane, Armchair, CheckCircle2, Lock } from 'lucide-react';

export default function SeatMap() {
    const { id: flightId } = useParams();
    const navigate = useNavigate();
    const { user } = useAuth();
    const [flight, setFlight] = useState(null);
    const [seats, setSeats] = useState([]);
    const [selectedSeats, setSelectedSeats] = useState([]);
    const [isLocking, setIsLocking] = useState(false);

    useEffect(() => {
        const fetchSeatMap = async () => {
            try {
                const res = await apiClient.get(`flights/${flightId}/seats/`);
                setFlight(res.data.flight);
                setSeats(res.data.seats);
            } catch (error) {
                console.error("Failed to load seats");
            }
        };
        fetchSeatMap();
    }, [flightId]);

    const handleSeatClick = (seat) => {
        if (selectedSeats.some(s => s.id === seat.id)) {
            setSelectedSeats(selectedSeats.filter(s => s.id !== seat.id));
        } else {
            if (selectedSeats.length >= 4) {
                alert("You can select a maximum of 4 seats per booking.");
                return;
            }
            setSelectedSeats([...selectedSeats, seat]);
        }
    };

    const handleLockAndProceed = async () => {
        if (!user) {
            alert("Please sign in to book a seat.");
            navigate('/login');
            return;
        }

        setIsLocking(true);
        try {
            await Promise.all(selectedSeats.map(seat => 
                apiClient.post(`flights/${flightId}/seats/${seat.id}/lock/`)
            ));
            navigate('/checkout', { 
                state: { flightId: flight.id, seats: selectedSeats } 
            });
        } catch (error) {
            alert(error.response?.data?.error || "One or more seats could not be secured. They might have just been taken!");
            const res = await apiClient.get(`flights/${flightId}/seats/`);
            setSeats(res.data.seats);
            setSelectedSeats([]);
        } finally {
            setIsLocking(false);
        }
    };

    if (!flight) return (
        <div className="min-h-screen bg-creame flex items-center justify-center">
            <div className="animate-pulse flex flex-col items-center">
                <Plane className="text-julianna mb-4 animate-bounce" size={48} />
                <p className="text-julianna font-bold text-xl">Loading Aircraft...</p>
            </div>
        </div>
    );
    const totalPrice = selectedSeats.reduce((sum, seat) => sum + parseFloat(seat.base_price), 0);

    return (
        <div className="min-h-[calc(100vh-80px)] bg-creame py-12 px-6">
            <div className="max-w-6xl mx-auto flex flex-col lg:flex-row gap-12">                
                <div className="flex-1 flex flex-col items-center">
                    <div className="flex gap-6 mb-8 bg-white px-8 py-4 rounded-full shadow-sm text-sm font-semibold text-gray-600">
                        <div className="flex items-center gap-2"><div className="w-4 h-4 rounded bg-white border-2 border-julianna"></div> Available</div>
                        <div className="flex items-center gap-2"><div className="w-4 h-4 rounded bg-addison"></div> Selected</div>
                        <div className="flex items-center gap-2"><div className="w-4 h-4 rounded bg-gray-300"></div> Booked/Locked</div>
                    </div>
                    <div className="bg-white p-8 rounded-[5rem] rounded-b-none border-[12px] border-pastelBlue shadow-2xl relative w-full max-w-md">
                        <div className="absolute -top-6 left-1/2 transform -translate-x-1/2 w-32 h-12 bg-pastelBlue rounded-t-full opacity-50"></div>
                        <h2 className="text-center font-black text-gray-300 tracking-widest mb-10 text-xl uppercase">Front</h2>
                        <div className="grid grid-cols-[1fr_1fr_2rem_1fr_1fr] gap-y-6 justify-items-center relative">
                            <div className="absolute top-0 bottom-0 left-1/2 transform -translate-x-1/2 w-8 bg-gray-50 rounded-full border border-dashed border-gray-200"></div>
                            {seats.map((seat, index) => {
                                const isSelected = selectedSeats.some(s => s.id === seat.id);
                                const isUnavailable = seat.status === 'locked' || seat.status === 'booked';
                                const isAisleSeat = index % 4 === 1;
                                return (
                                    <div key={seat.id} className="contents">
                                        <button disabled={isUnavailable} onClick={() => handleSeatClick(seat)} 
                                            className={`
                                                relative w-12 h-14 rounded-t-xl rounded-b-md font-bold text-sm transition-all duration-200 flex flex-col items-center justify-center
                                                ${isSelected ? 'bg-addison text-white shadow-lg transform scale-110 ring-4 ring-compassion' : ''}
                                                ${isUnavailable ? 'bg-gray-200 text-gray-400 cursor-not-allowed' : ''}
                                                ${!isSelected && !isUnavailable ? 'bg-white text-gray-700 hover:bg-compassion border-2 border-julianna hover:border-addison shadow-sm' : ''}
                                            `}
                                        >
                                            <span className="z-10">{seat.seat_number}</span>
                                            <div className={`absolute bottom-1 w-8 h-2 rounded-full opacity-30 ${isSelected ? 'bg-white' : 'bg-gray-400'}`}></div>
                                        </button>
                                        {isAisleSeat && <div className="w-8"></div>}
                                    </div>
                                );
                            })}
                        </div>
                    </div>
                </div>                
                <div className="flex-1 lg:max-w-sm pt-10">
                    <div className="bg-white p-8 rounded-3xl shadow-xl border-t-8 border-julianna sticky top-24">
                        <div className="flex justify-between items-start mb-6 border-b border-gray-100 pb-6">
                            <div>
                                <h2 className="text-3xl font-black text-gray-800 tracking-tight">{flight.flight_number}</h2>
                                <p className="text-gray-500 font-medium mt-1">{flight.source} <span className="text-julianna">→</span> {flight.destination}</p>
                            </div>
                            <div className="bg-pastelBlue p-3 rounded-2xl text-julianna">
                                <Armchair size={28} />
                            </div>
                        </div>
                        {selectedSeats.length > 0 ? (
                            <div className="animate-fade-in-up">
                                <div className="bg-compassion/50 p-6 rounded-2xl border border-addison/30 mb-8 max-h-64 overflow-y-auto">
                                    <div className="flex justify-between items-center mb-4 border-b border-addison/30 pb-2">
                                        <span className="text-gray-600 font-bold">Selected Seats ({selectedSeats.length}/4)</span>
                                    </div>
                                    {selectedSeats.map(seat => (
                                        <div key={seat.id} className="flex justify-between items-center mb-3">
                                            <div>
                                                <span className="text-xl font-black text-gray-900">{seat.seat_number}</span>
                                                <span className="text-xs font-semibold text-gray-500 ml-2 capitalize bg-white px-2 py-1 rounded shadow-sm">{seat.seat_class}</span>
                                            </div>
                                            <span className="font-bold text-gray-800">₹{seat.base_price}</span>
                                        </div>
                                    ))}
                                    <div className="flex justify-between items-center pt-4 mt-4 border-t border-addison/30">
                                        <span className="text-gray-600 font-medium">Total Price</span>
                                        <span className="text-3xl font-black text-julianna">₹{totalPrice.toFixed(2)}</span>
                                    </div>
                                </div> 
                                <button onClick={handleLockAndProceed} disabled={isLocking}
                                    className="w-full bg-julianna text-white py-4 rounded-xl font-bold text-lg shadow-lg hover:shadow-xl hover:-translate-y-1 hover:bg-opacity-90 disabled:opacity-50 disabled:transform-none transition-all flex justify-center items-center gap-2">
                                    {isLocking ? (
                                        <><Lock className="animate-pulse" size={20} /> Securing Seats...</>
                                    ) : (
                                        <><CheckCircle2 size={20} /> Continue to Payment</>
                                    )}
                                </button>
                                <p className="text-center text-xs text-gray-400 mt-4 font-medium flex items-center justify-center gap-1">
                                    <Lock size={12} /> Seats will be locked for 10 minutes
                                </p>
                            </div>
                        ) : (
                            <div className="h-64 flex flex-col items-center justify-center text-center border-2 border-dashed border-gray-200 rounded-2xl bg-gray-50">
                                <Armchair size={48} className="text-gray-300 mb-4" />
                                <p className="text-gray-500 font-medium">Select up to 4 seats from the map<br/>to view pricing and continue.</p>
                            </div>
                        )}
                    </div>
                </div>
            </div>
        </div>
    );
}