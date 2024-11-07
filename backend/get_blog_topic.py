import random

#Ideally this wouldn't be hardcoded. I looked into Google trends, Google Search API, Google Places API and hardcoding seemed like the best option.
#I could always find a way to programmatically add more unique locations in the future.
destinations = [
    # Major Cities
    "Tokyo, Japan", "New York City, USA", "Paris, France", "London, England", 
    "Rome, Italy", "Sydney, Australia", "Berlin, Germany", "Los Angeles, USA", 
    "Barcelona, Spain", "Istanbul, Turkey", "Seoul, South Korea", "Bangkok, Thailand", 
    "Mexico City, Mexico", "Rio de Janeiro, Brazil", "Cairo, Egypt", "Moscow, Russia", 
    "Mumbai, India", "Beijing, China", "Toronto, Canada", "Cape Town, South Africa", 

    # Small/Quirky Spots
    "Eureka Springs, USA", "Marfa, USA", "San Miguel de Allende, Mexico", 
    "Chefchaouen, Morocco", "Ubud, Bali, Indonesia", "Hoi An, Vietnam", 
    "Hallstatt, Austria", "Sintra, Portugal", "Siem Reap, Cambodia", 
    "Rothenburg ob der Tauber, Germany", "Siena, Italy", "Queenstown, New Zealand", 
    "Gimmelwald, Switzerland", "Luang Prabang, Laos", "Lunenburg, Canada", 
    "Reykjavik, Iceland", "Ghent, Belgium", "Kotor, Montenegro", "Cusco, Peru", 

    # Unique Points of Interest
    "Mount Kilimanjaro, Tanzania", "Grand Canyon, USA", "Great Wall of China, China", 
    "Santorini, Greece", "Petra, Jordan", "Machu Picchu, Peru", "Uluru, Australia", 
    "Banff National Park, Canada", "Antelope Canyon, USA", "Salar de Uyuni, Bolivia", 
    "Lake Bled, Slovenia", "Angkor Wat, Cambodia", "Galapagos Islands, Ecuador", 
    "Blue Lagoon, Iceland", "Pamukkale, Turkey", "Taj Mahal, India", 
    "Avenue of the Baobabs, Madagascar", "Plitvice Lakes, Croatia", 

    # Local Festivals & Events
    "Carnival in Rio de Janeiro, Brazil", "Oktoberfest in Munich, Germany", 
    "Dia de los Muertos in Oaxaca, Mexico", "Songkran Festival in Chiang Mai, Thailand", 
    "Mardi Gras in New Orleans, USA", "Cherry Blossom Festival in Kyoto, Japan", 
    "Running of the Bulls in Pamplona, Spain", "La Tomatina in Buñol, Spain", 
    "Loi Krathong in Chiang Mai, Thailand", "Burning Man in Black Rock Desert, USA", 
    "Edinburgh Festival Fringe, Scotland", "Harbin Ice Festival, China", 
    "Albuquerque International Balloon Fiesta, USA", "Diwali Festival in Jaipur, India", 
    "Sapporo Snow Festival, Japan", "Holi Festival in Mathura, India", 
    "Venice Carnival, Italy", "Cannes Film Festival, France", "Montreux Jazz Festival, Switzerland", 

    # Miscellaneous Interesting Spots
    "Santorini's Caldera, Greece", "Aurora Borealis in Tromsø, Norway", 
    "Easter Island, Chile", "Patagonia, Argentina", "Tikal, Guatemala", 
    "Zakynthos Shipwreck Beach, Greece", "Torres del Paine, Chile", 
    "Old Havana, Cuba", "Lofoten Islands, Norway", "Okavango Delta, Botswana", 
    "Cinque Terre, Italy", "Great Barrier Reef, Australia", 
    "Lake Baikal, Russia", "Dubrovnik Old Town, Croatia", "The Colosseum, Italy", 
    "Yellowstone National Park, USA", "Chichen Itza, Mexico", "Ephesus, Turkey", 

    # North America
    "San Francisco, USA", "Washington D.C., USA", "Vancouver, Canada", 
    "Tulum, Mexico", "Banff, Canada", "Quebec City, Canada", 
    "Nashville, USA", "Austin, USA", "Charleston, USA", 
    "Sedona, USA", "Savannah, USA", "Las Vegas, USA", 
    "Miami, USA", "Yosemite National Park, USA", "Niagara Falls, Canada/USA", 

    # Europe
    "Prague, Czech Republic", "Dubrovnik, Croatia", "Budapest, Hungary", 
    "Lisbon, Portugal", "Amsterdam, Netherlands", "Florence, Italy", 
    "Vienna, Austria", "Krakow, Poland", "Edinburgh, Scotland", 
    "Bruges, Belgium", "Tallinn, Estonia", "Riga, Latvia", 
    "Dublin, Ireland", "Stockholm, Sweden", "Helsinki, Finland", 
    "Copenhagen, Denmark", "Lucerne, Switzerland", "Athens, Greece", 

    # Asia
    "Kyoto, Japan", "Hong Kong, China", "Singapore", 
    "Kuala Lumpur, Malaysia", "Phuket, Thailand", "Hanoi, Vietnam", 
    "Jaipur, India", "Kathmandu, Nepal", "Borneo, Malaysia", 
    "Boracay, Philippines", "Ninh Binh, Vietnam", "Mandalay, Myanmar", 

    # Africa
    "Cape Town, South Africa", "Zanzibar, Tanzania", "Marrakech, Morocco", 
    "Victoria Falls, Zimbabwe/Zambia", "Chefchaouen, Morocco", 
    "Namib Desert, Namibia", "Pyramids of Giza, Egypt", 

    # South America
    "Buenos Aires, Argentina", "Lima, Peru", "Cartagena, Colombia", 
    "Santiago, Chile", "Quito, Ecuador", "Bogota, Colombia", 
    "Rio de Janeiro, Brazil", "La Paz, Bolivia", "Montevideo, Uruguay", 

    # Australia & Pacific
    "Auckland, New Zealand", "Melbourne, Australia", "Brisbane, Australia", 
    "Tasmania, Australia", "Fiji Islands", "Bora Bora, French Polynesia", 
    "Rarotonga, Cook Islands", "Gold Coast, Australia", "Wellington, New Zealand"

    # Big US Cities
    "Chicago, Illinois", "Boston, Massachusetts", "Seattle, Washington", 
    "San Diego, California", "Houston, Texas", "Denver, Colorado", 
    "Portland, Oregon", "Atlanta, Georgia", "Minneapolis, Minnesota", 
    "Philadelphia, Pennsylvania", "Detroit, Michigan", "Phoenix, Arizona", 
    "Salt Lake City, Utah", "Baltimore, Maryland", 

    # Small US Towns and Cities
    "Asheville, North Carolina", "Santa Fe, New Mexico", "Burlington, Vermont", 
    "Key West, Florida", "Sedona, Arizona", "Bozeman, Montana", 
    "Taos, New Mexico", "St. Augustine, Florida", "Fredericksburg, Texas", 
    "Bar Harbor, Maine", "Carmel-by-the-Sea, California", "Traverse City, Michigan", 
    "Newport, Rhode Island", "Greenville, South Carolina", "Galena, Illinois", 

    # US Hiking/Camping Locations
    "Yosemite National Park, California", "Zion National Park, Utah", 
    "Grand Teton National Park, Wyoming", "Appalachian Trail, Georgia to Maine", 
    "Mount Rainier National Park, Washington", "Rocky Mountain National Park, Colorado", 
    "Acadia National Park, Maine", "Great Smoky Mountains, Tennessee/North Carolina", 
    "Big Sur, California", "Joshua Tree National Park, California", 
    "Glacier National Park, Montana", "Bryce Canyon, Utah", 
    "Shenandoah National Park, Virginia", "Denali National Park, Alaska", 
    "Great Sand Dunes National Park, Colorado", "Olympic National Park, Washington", 

    # US Camping/Outdoor Adventure
    "Adirondack Mountains, New York", "Boundary Waters Canoe Area, Minnesota", 
    "Ozark National Forest, Arkansas", "White Mountains, New Hampshire", 
    "Blue Ridge Parkway, Virginia/North Carolina", "Lake Tahoe, California/Nevada", 
    "The Black Hills, South Dakota", "Mammoth Cave National Park, Kentucky", 
    "Cumberland Island, Georgia", "Everglades National Park, Florida", 

    # US Festivals and Events
    "Coachella Music Festival, California", "South by Southwest (SXSW), Texas", 
    "New Orleans Jazz & Heritage Festival, Louisiana", "Burning Man, Nevada", 
    "Albuquerque International Balloon Fiesta, New Mexico", "Kentucky Derby, Louisville, Kentucky", 
    "Sturgis Motorcycle Rally, South Dakota", "Austin City Limits Music Festival, Texas", 
    "Boston Marathon, Massachusetts", "New York Comic Con, New York", 
    "Mardi Gras, Louisiana", "Oregon Shakespeare Festival, Ashland, Oregon", 
    "Rose Parade, Pasadena, California", "Aloha Festival, Hawaii", 
    "Telluride Film Festival, Colorado", "The Great American Beer Festival, Denver, Colorado", 
    "Sundance Film Festival, Utah", "Lollapalooza, Chicago, Illinois", 
    "Seattle International Film Festival, Washington", 

    # US Beaches & Coastal Locations
    "Myrtle Beach, South Carolina", "Outer Banks, North Carolina", 
    "Malibu, California", "Naples, Florida", "Hilton Head Island, South Carolina", 
    "Gulf Shores, Alabama", "Santa Monica, California", "Destin, Florida", 
    "Cannon Beach, Oregon", "Virginia Beach, Virginia", 

    # Miscellaneous Unique US Spots
    "Niagara Falls, New York", "Badlands National Park, South Dakota", 
    "Monument Valley, Arizona/Utah", "Antelope Canyon, Arizona", 
    "Lake Powell, Utah/Arizona", "Great Basin National Park, Nevada", 
    "Death Valley National Park, California/Nevada", "Sequoia National Park, California", 
    "Hot Springs National Park, Arkansas", "Craters of the Moon National Monument, Idaho"
]

def get_blog_topic():
    return random.choice(destinations)




