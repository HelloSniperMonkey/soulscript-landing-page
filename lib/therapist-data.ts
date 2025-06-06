import { Therapist } from '@/types/therapist'

export const therapistsData: Therapist[] = [
  {
    id: "1",
    name: "Dr. Sarah Johnson",
    specialization: ["Anxiety", "Depression", "Cognitive Behavioral Therapy"],
    rating: 4.8,
    reviewCount: 127,
    yearsOfExperience: 12,
    bio: "Dr. Sarah Johnson is a licensed clinical psychologist with over 12 years of experience helping individuals overcome anxiety and depression. She specializes in Cognitive Behavioral Therapy and has helped hundreds of clients achieve their mental health goals.",
    imageUrl: "/placeholder-user.jpg",
    location: {
      lat: 40.7831,
      lng: -73.9712,
      address: "123 Manhattan Ave",  
      city: "New York",
      state: "NY",
      zipCode: "10025"
    },
    contact: {
      phone: "(555) 123-4567",
      email: "sarah.johnson@therapy.com",
      website: "www.sarahjohnsontherapy.com"
    },
    availability: {
      days: ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"],
      timeSlots: ["9:00 AM", "11:00 AM", "2:00 PM", "4:00 PM"]
    },
    sessionType: ["in-person", "online"],
    fees: {
      consultationFee: 100,
      sessionFee: 150,
      currency: "USD"
    },
    languages: ["English", "Spanish"],
    education: ["PhD in Clinical Psychology - Columbia University"],
    certifications: ["Licensed Clinical Psychologist", "CBT Certified"]
  },
  {
    id: "2", 
    name: "Dr. Michael Chen",
    specialization: ["Trauma Therapy", "PTSD", "Mindfulness-Based Therapy"],
    rating: 4.9,
    reviewCount: 89,
    yearsOfExperience: 8,
    bio: "Dr. Michael Chen specializes in trauma therapy and PTSD treatment. He uses evidence-based approaches including EMDR and mindfulness-based interventions to help clients heal from traumatic experiences.",
    imageUrl: "/placeholder-user.jpg",
    location: {
      lat: 40.7505,
      lng: -73.9934,
      address: "456 Therapy Lane",
      city: "New York", 
      state: "NY",
      zipCode: "10001"
    },
    contact: {
      phone: "(555) 234-5678",
      email: "michael.chen@therapy.com"
    },
    availability: {
      days: ["Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"],
      timeSlots: ["10:00 AM", "1:00 PM", "3:00 PM", "5:00 PM"]
    },
    sessionType: ["in-person", "online"],
    fees: {
      consultationFee: 120,
      sessionFee: 175,
      currency: "USD"
    },
    languages: ["English", "Mandarin"],
    education: ["PsyD in Clinical Psychology - NYU"],
    certifications: ["Licensed Psychologist", "EMDR Certified"]
  },
  {
    id: "3",
    name: "Dr. Emily Rodriguez",
    specialization: ["Family Therapy", "Couples Counseling", "Child Psychology"],
    rating: 4.7,
    reviewCount: 156,
    yearsOfExperience: 15,
    bio: "Dr. Emily Rodriguez is a family therapist with extensive experience in couples counseling and child psychology. She helps families navigate challenges and build stronger relationships through evidence-based therapeutic approaches.",
    imageUrl: "/placeholder-user.jpg",
    location: {
      lat: 40.7282,
      lng: -73.7949,
      address: "789 Family Center Dr",
      city: "Queens",
      state: "NY", 
      zipCode: "11375"
    },
    contact: {
      phone: "(555) 345-6789",
      email: "emily.rodriguez@therapy.com",
      website: "www.familytherapynyc.com"
    },
    availability: {
      days: ["Monday", "Wednesday", "Thursday", "Friday", "Saturday"],
      timeSlots: ["9:00 AM", "12:00 PM", "3:00 PM", "6:00 PM"]
    },
    sessionType: ["in-person"],
    fees: {
      consultationFee: 90,
      sessionFee: 140,
      currency: "USD"
    },
    languages: ["English", "Spanish"],
    education: ["PhD in Family Psychology - Fordham University"],
    certifications: ["Licensed Marriage and Family Therapist", "Child Psychology Specialist"]
  },
  {
    id: "4",
    name: "Dr. James Wilson",
    specialization: ["Addiction Counseling", "Substance Abuse", "Group Therapy"],
    rating: 4.6,
    reviewCount: 203,
    yearsOfExperience: 20,
    bio: "Dr. James Wilson has over 20 years of experience in addiction counseling and substance abuse treatment. He leads both individual and group therapy sessions, helping clients on their journey to recovery.",
    imageUrl: "/placeholder-user.jpg",
    location: {
      lat: 40.6782,
      lng: -73.9442,
      address: "321 Recovery Ave",
      city: "Brooklyn",
      state: "NY",
      zipCode: "11238"
    },
    contact: {
      phone: "(555) 456-7890",
      email: "james.wilson@therapy.com"
    },
    availability: {
      days: ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"],
      timeSlots: ["8:00 AM", "10:00 AM", "2:00 PM", "4:00 PM", "6:00 PM"]
    },
    sessionType: ["in-person", "both"],
    fees: {
      consultationFee: 80,
      sessionFee: 120,
      currency: "USD"
    },
    languages: ["English"],
    education: ["MS in Counseling Psychology - Teachers College"],
    certifications: ["Licensed Addiction Counselor", "Group Therapy Specialist"]
  },
  {
    id: "5",
    name: "Dr. Lisa Park",
    specialization: ["Teen Counseling", "Eating Disorders", "Self-Esteem"],
    rating: 4.9,
    reviewCount: 74,
    yearsOfExperience: 9,
    bio: "Dr. Lisa Park specializes in working with teenagers and young adults, focusing on eating disorders, self-esteem issues, and identity development. She creates a safe and supportive environment for young clients to explore their challenges.",
    imageUrl: "/placeholder-user.jpg",
    location: {
      lat: 40.8518,
      lng: -73.8370,
      address: "654 Youth Center Blvd",
      city: "Bronx",
      state: "NY",
      zipCode: "10461"
    },
    contact: {
      phone: "(555) 567-8901",
      email: "lisa.park@therapy.com",
      website: "www.teencounselingnyc.com"
    },
    availability: {
      days: ["Tuesday", "Wednesday", "Thursday", "Friday"],
      timeSlots: ["11:00 AM", "1:00 PM", "3:00 PM", "5:00 PM"]
    },
    sessionType: ["online", "both"],
    fees: {
      consultationFee: 110,
      sessionFee: 160,
      currency: "USD"
    },
    languages: ["English", "Korean"],
    education: ["PhD in Adolescent Psychology - Yeshiva University"],
    certifications: ["Licensed Clinical Social Worker", "Eating Disorder Specialist"]
  }
]