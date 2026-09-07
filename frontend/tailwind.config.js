/** @type {import('tailwindcss').Config} */
export default {
    content: [
        "./index.html",
        "./src/**/*.{js,ts,jsx,tsx}",
    ],
    theme: {
        extend: {
            colors: {
                story: {
                    blue: '#E0F2FE', // Light sky blue
                    lavender: '#E9D5FF', // Soft purple
                    cream: '#FFFBEB', // Warm paper
                    pink: '#FCE7F3', // Gentle pink
                    text: '#4B5563', // Soft gray for text
                    dark: '#1F2937', // Darker gray for headings
                    accent: '#8B5CF6', // Primary purple accent
                    secondary: '#EC4899', // Secondary pink accent
                    highlight: '#FDE68A', // Yellow/Gold for stars
                }
            },
            fontFamily: {
                sans: ['"Inter"', 'sans-serif'],
                heading: ['"Outfit"', 'sans-serif'], // We will need to load this
                hand: ['"Patrick Hand"', 'cursive'], // For storybook feel
            },
            backgroundImage: {
                'cloud-pattern': "url('https://www.transparenttextures.com/patterns/clouds.png')", // Or CSS radial gradient
                'magical-gradient': 'linear-gradient(to bottom right, #E0F2FE, #E9D5FF, #FFFBEB)',
            },
            boxShadow: {
                'soft': '0 10px 40px -10px rgba(0,0,0,0.08)',
                'glow': '0 0 20px rgba(139, 92, 246, 0.3)',
            }
        },
    },
    plugins: [],
}
