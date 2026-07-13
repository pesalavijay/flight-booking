import { useState, useEffect } from 'react';
import { useLocation, useNavigate, Navigate } from 'react-router-dom';
import apiClient from '../api/client';
import { useAuth } from '../context/AuthContext';
import { ShieldCheck, PlaneTakeoff, Loader2, Users, CreditCard, Clock } from 'lucide-react';

export default function Checkout() {
    const location = useLocation();
    const navigate = useNavigate();
    const { user } = useAuth();
    const { flightId, seats } = location.state || { seats: [] };
    if (!location.state || seats.length === 0) {
        return <Navigate to="/" replace />;
    }

    const [passengers, setPassengers] = useState(
        seats.map(seat => ({
            seat_id: seat.id,
            seat_number: seat.seat_number,
            passenger_name: '',
            passenger_age: ''
        }))
    );
    
    const [isProcessing, setIsProcessing] = useState(false);    
    const [timeLeft, setTimeLeft] = useState(600);
    const totalBasePrice = seats.reduce((sum, seat) => sum + parseFloat(seat.base_price), 0);
    useEffect(() => {
        if (timeLeft <= 0) {
            alert("Time is up! Your seat reservation has expired.");
            navigate(-1); 
            return;
        }
        const timerId = setInterval(() => {
            setTimeLeft(prev => prev - 1);
        }, 1000);
        return () => clearInterval(timerId);
    }, [timeLeft, navigate]);

    const mins = Math.floor(timeLeft / 60);
    const secs = timeLeft % 60;
    const showTime = `${mins}:${secs < 10 ? '0' : ''}${secs}`;

    const handleInputChange = (index, field, value) => {
        const updatedPassengers = [...passengers];
        updatedPassengers[index][field] = value;
        setPassengers(updatedPassengers);
    };

    const initializeRazorpay = () => {
        return new Promise((resolve) => {
            const script = document.createElement('script');
            script.src = 'https://checkout.razorpay.com/v1/checkout.js';
            script.onload = () => resolve(true);
            script.onerror = () => resolve(false);
            document.body.appendChild(script);
        });
    };

    const handleCheckout = async (e) => {
        e.preventDefault();
        setIsProcessing(true);
        const res = await initializeRazorpay();
        if (!res) {
            alert('Razorpay SDK failed to load');
            setIsProcessing(false);
            return;
        }
        try {
            const bookingResponse = await apiClient.post('create/', {
                flight_id: flightId,
                passengers: passengers 
            });
            const { payment } = bookingResponse.data;
            const options = {
                key: import.meta.env.VITE_RAZORPAY_KEY_ID, 
                amount: payment.amount * 100,
                currency: payment.currency,
                name: 'Platter Airways',
                description: `Flight Booking - ${seats.length} Seats`,
                order_id: payment.razorpay_order_id,
                handler: async function (response) {
                    try {
                        await apiClient.post('verify-payment/', {
                            razorpay_order_id: payment.razorpay_order_id, 
                            razorpay_payment_id: response.razorpay_payment_id,
                            razorpay_signature: response.razorpay_signature
                        });
                        
                        alert('Group Booking Confirmed!');
                        navigate('/my-bookings');
                    } catch (verifyError) {
                        alert('Payment verification failed.');
                    }
                },
                prefill: {
                    name: user?.full_name || '',
                    email: user?.email || '',
                },
                theme: { color: '#768EEB' }
            };
            const paymentObject = new window.Razorpay(options);
            paymentObject.open();
        } catch (error) {
            alert(error.response?.data?.error || 'Failed to initiate booking');
        } finally {
            setIsProcessing(false);
        }
    };
    return (
        <div className="min-h-[calc(100vh-80px)] bg-creame py-12 px-6" >
            <div className="max-w-5xl mx-auto grid grid-cols-1 md:grid-cols-2 gap-10" >
                <div className="bg-white p-8 rounded-3xl shadow-xl border-t-8 border-julianna" >
                    <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-xl flex justify-between items-center mb-6 shadow-sm">
                        <span className="font-semibold flex items-center gap-2">
                            <Clock size={18} /> Complete booking in
                        </span>
                        <span className="text-lg font-mono font-black tracking-wider text-red-600" >
                            {showTime}
                        </span>
                    </div>
                    <div className="flex items-center gap-3 mb-8 border-b border-gray-100 pb-4" >
                        <Users className="text-julianna" size={32} />
                        <h2 className="text-2xl font-black text-gray-800" > Passenger Details </h2>
                    </div>
                    <form onSubmit={handleCheckout}>
                        <div className="space-y-6">
                            {passengers.map((passenger, index) => (
                                <div key={passenger.seat_id} className="bg-gray-50 p-5 rounded-2xl border border-gray-100">
                                    <div className="flex justify-between items-center mb-4">
                                        <h3 className="font-bold text-gray-800">Passenger {index + 1}</h3>
                                        <span className="bg-pastelBlue/30 text-julianna px-3 py-1 rounded-lg text-sm font-bold">
                                            Seat {passenger.seat_number}
                                        </span>
                                    </div>
                                    <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
                                        <div className="sm:col-span-2">
                                            <label className="block text-xs font-semibold text-gray-500 mb-1">Full Name</label>
                                            <input required type="text" placeholder="As per Government ID" value={passenger.passenger_name} 
                                                onChange={(e) => handleInputChange(index, 'passenger_name', e.target.value)}
                                                className="w-full px-4 py-3 rounded-xl border-2 border-gray-200 focus:border-pastelBlue focus:outline-none transition-colors" 
                                            />
                                        </div>
                                        <div>
                                            <label className="block text-xs font-semibold text-gray-500 mb-1">Age</label>
                                            <input required type="number" min="1" placeholder="e.g. 28" value={passenger.passenger_age}
                                                onChange={(e) => handleInputChange(index, 'passenger_age', e.target.value)}
                                                className="w-full px-4 py-3 rounded-xl border-2 border-gray-200 focus:border-pastelBlue focus:outline-none transition-colors" 
                                            />
                                        </div>
                                    </div>
                                </div>
                            ))}
                        </div>
                        <button type="submit" disabled={isProcessing} className="w-full bg-julianna text-white py-4 rounded-xl font-bold text-lg shadow-lg hover:shadow-xl hover:-translate-y-1 hover:bg-opacity-90 disabled:opacity-50 disabled:transform-none transition-all flex justify-center items-center gap-2 mt-8 cursor-pointer">
                            {isProcessing ? (
                                <><Loader2 className="animate-spin" size={24} /> Securing Gateway... </>
                            ) : (
                                <><CreditCard size={24} /> Pay ₹ {totalBasePrice.toFixed(2)} via Razorpay </>
                            )}
                        </button>
                    </form>
                </div>
                <div className="bg-compassion/30 p-8 rounded-3xl border-2 border-addison/20 h-fit sticky top-24">
                    <div className="flex items-center gap-3 mb-6">
                        <div className="bg-white p-2 rounded-xl text-addison shadow-sm">
                            <PlaneTakeoff size={24} />
                        </div>
                        <h3 className="text-xl font-black text-gray-800">Booking Summary</h3>
                    </div>
                    <div className="bg-white rounded-2xl p-6 shadow-sm mb-6">
                        <div className="flex justify-between items-center pb-4 border-b border-gray-100 mb-4">
                            <span className="text-gray-500 font-medium">Flight ID</span>
                            <span className="font-bold text-gray-800">#{flightId}</span>
                        </div>
                        <div className="space-y-3 mb-4">
                            <span className="text-gray-500 font-medium block mb-2">Selected Seats</span>
                            {seats.map(seat => (
                                <div key={seat.id} className="flex justify-between items-center text-sm">
                                    <span className="font-bold text-gray-800 bg-gray-100 px-2 py-1 rounded">Seat {seat.seat_number} </span>
                                    <span className="font-semibold text-gray-600">₹{parseFloat(seat.base_price).toFixed(2)} </span>
                                </div>
                            ))}
                        </div>
                        <div className="pt-4 border-t border-gray-100 border-dashed" >
                            <div className="flex justify-between items-center text-sm" >
                                <span className="text-gray-500"> Total Base Fare </span>
                                <span className="font-semibold text-gray-800"> ₹ {totalBasePrice.toFixed(2)} </span>
                            </div>
                        </div>
                    </div>
                    <div className="flex justify-between items-center bg-addison text-white p-6 rounded-2xl shadow-md">
                        <span className="font-medium">Total Amount</span>
                        <span className="text-3xl font-black"> ₹{totalBasePrice.toFixed(2)} </span>
                    </div>
                </div>
            </div>
        </div>
    );
}