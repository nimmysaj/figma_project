# app1/management/commands/populate_districts.py

from django.core.management.base import BaseCommand
from Accounts.models import State, District

class Command(BaseCommand):
    help = 'Populates the District model with districts for Kerala, Tamil Nadu, and Karnataka'

    # District data for specific states
    DISTRICTS = {
        "Kerala": [
            "Alappuzha", "Ernakulam", "Idukki", "Kannur", "Kasaragod", 
            "Kollam", "Kottayam", "Kozhikode", "Malappuram", "Palakkad", 
            "Pathanamthitta", "Thiruvananthapuram", "Thrissur", "Wayanad"
        ],
        "Tamil Nādu": [
            "Ariyalur", "Chengalpattu", "Chennai", "Coimbatore", "Cuddalore", 
            "Dharmapuri", "Dindigul", "Erode", "Kallakurichi", "Kancheepuram", 
            "Karur", "Krishnagiri", "Madurai", "Nagapattinam", "Namakkal", 
            "Nilgiris", "Perambalur", "Pudukkottai", "Ramanathapuram", 
            "Ranipet", "Salem", "Sivaganga", "Tenkasi", "Thanjavur", 
            "Theni", "Thoothukudi", "Tiruchirappalli", "Tirunelveli", 
            "Tirupathur", "Tiruppur", "Tiruvallur", "Tiruvannamalai", 
            "Tiruvarur", "Vellore", "Viluppuram", "Virudhunagar"
        ],
        "Karnātaka": [
            "Bagalkot", "Ballari", "Belagavi", "Bengaluru Rural", 
            "Bengaluru Urban", "Bidar", "Chamarajanagar", "Chikballapur", 
            "Chikkamagaluru", "Chitradurga", "Dakshina Kannada", "Davangere", 
            "Dharwad", "Gadag", "Hassan", "Haveri", "Kalaburagi", "Kodagu", 
            "Kolar", "Koppal", "Mandya", "Mysuru", "Raichur", "Ramanagara", 
            "Shivamogga", "Tumakuru", "Udupi", "Uttara Kannada", "Vijayapura", 
            "Yadgir"
        ],
         "Andhra Pradesh": [
            "Anantapur", "Chittoor", "East Godavari", "Guntur", 
            "Krishna", "Kurnool", "Prakasam", "Srikakulam", "Visakhapatnam", 
            "Vizianagaram", "West Godavari", "YSR Kadapa"
        ],
        "Arunāchal Pradesh": [
            "Anjaw", "Changlang", "East Kameng", "East Siang", "Kamle", 
            "Kra Daadi", "Kurung Kumey", "Lepa Rada", "Lohit", "Longding", 
            "Lower Dibang Valley", "Lower Siang", "Lower Subansiri", "Namsai", 
            "Pakke-Kessang", "Papum Pare", "Shi Yomi", "Siang", "Tawang", "Tirap", 
            "Upper Dibang Valley", "Upper Siang", "Upper Subansiri", "West Kameng", 
            "West Siang"
        ],
        "Assam": [
            "Baksa", "Barpeta", "Biswanath", "Bongaigaon", "Cachar", "Charaideo", 
            "Chirang", "Darrang", "Dhemaji", "Dhubri", "Dibrugarh", "Goalpara", 
            "Golaghat", "Hailakandi", "Hojai", "Jorhat", "Kamrup", "Kamrup Metropolitan", 
            "Karbi Anglong", "Karimganj", "Kokrajhar", "Lakhimpur", "Majuli", "Morigaon", 
            "Nagaon", "Nalbari", "Sivasagar", "Sonitpur", "South Salmara-Mankachar", 
            "Tinsukia", "Udalguri", "West Karbi Anglong"
        ],
        "Bihār": [
            "Araria", "Arwal", "Aurangabad", "Banka", "Begusarai", "Bhagalpur", 
            "Bhojpur", "Buxar", "Darbhanga", "East Champaran", "Gaya", "Gopalganj", 
            "Jamui", "Jehanabad", "Kaimur", "Katihar", "Khagaria", "Kishanganj", 
            "Lakhisarai", "Madhepura", "Madhubani", "Munger", "Muzaffarpur", 
            "Nalanda", "Nawada", "Patna", "Purnia", "Rohtas", "Saharsa", 
            "Samastipur", "Saran", "Sheikhpura", "Sheohar", "Sitamarhi", "Siwan", 
            "Supaul", "Vaishali", "West Champaran"
        ],
        "Chhattīsgarh": [
            "Balod", "Baloda Bazar", "Balrampur", "Bastar", "Bemetara", "Bijapur", 
            "Bilaspur", "Dantewada", "Dhamtari", "Durg", "Gariaband", "Janjgir-Champa", 
            "Jashpur", "Kabirdham", "Kanker", "Kondagaon", "Korba", "Koriya", 
            "Mahasamund", "Mungeli", "Narayanpur", "Raigarh", "Raipur", 
            "Rajnandgaon", "Sukma", "Surajpur", "Surguja"
        ],
        "Goa": [
            "North Goa", "South Goa"
        ],
        "Gujarāt": [
            "Ahmedabad", "Amreli", "Anand", "Aravalli", "Banaskantha", "Bharuch", 
            "Bhavnagar", "Botad", "Chhota Udaipur", "Dahod", "Dang", "Devbhoomi Dwarka", 
            "Gandhinagar", "Gir Somnath", "Jamnagar", "Junagadh", "Kheda", "Kutch", 
            "Mahisagar", "Mehsana", "Morbi", "Narmada", "Navsari", "Panchmahal", 
            "Patan", "Porbandar", "Rajkot", "Sabarkantha", "Surat", "Surendranagar", 
            "Tapi", "Vadodara", "Valsad"
        ],
        "Haryāna": [
            "Ambala", "Bhiwani", "Charkhi Dadri", "Faridabad", "Fatehabad", "Gurugram", 
            "Hisar", "Jhajjar", "Jind", "Kaithal", "Karnal", "Kurukshetra", "Mahendragarh", 
            "Mewat", "Palwal", "Panchkula", "Panipat", "Rewari", "Rohtak", 
            "Sirsa", "Sonipat", "Yamunanagar"
        ],
        "Himāchal Pradesh": [
            "Bilaspur", "Chamba", "Hamirpur", "Kangra", "Kinnaur", "Kullu", 
            "Lahaul and Spiti", "Mandi", "Shimla", "Sirmaur", "Solan", "Una"
        ],
        "Jhārkhand": [
            "Bokaro", "Chatra", "Deoghar", "Dhanbad", "Dumka", "East Singhbhum", 
            "Garhwa", "Giridih", "Godda", "Gumla", "Hazaribagh", "Jamtara", 
            "Khunti", "Koderma", "Latehar", "Lohardaga", "Pakur", "Palamu", 
            "Ramgarh", "Ranchi", "Sahibganj", "Seraikela Kharsawan", "Simdega", 
            "West Singhbhum"
        ]
    }

    def handle(self, *args, **kwargs):
        for state_name, districts in self.DISTRICTS.items():
            try:
                state = State.objects.get(name=state_name)
            except State.DoesNotExist:
                self.stdout.write(self.style.WARNING(f"State '{state_name}' not found. Skipping districts for this state."))
                continue

            for district_name in districts:
                # Check for existing records to avoid duplicates
                existing_district = District.objects.filter(name=district_name, state=state).first()
                if existing_district:
                    self.stdout.write(self.style.WARNING(f"Duplicate district found: {district_name} in {state_name}. Skipping..."))
                    continue

                # Create district record
                District.objects.create(name=district_name, state=state)
                self.stdout.write(self.style.SUCCESS(f"Added district: {district_name} in {state_name}"))

        self.stdout.write(self.style.SUCCESS("Successfully populated District model with districts for Kerala, Tamil Nadu, and Karnataka"))
