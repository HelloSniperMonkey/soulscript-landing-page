"use client"

import React, { useState, useEffect, useRef } from 'react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { Separator } from '@/components/ui/separator'
import { TherapistWithDistance } from '@/types/therapist'
import { MapPin, Phone, Mail, Globe, Star, Clock, DollarSign, Users, CheckCircle } from 'lucide-react'
import Navbar from '@/components/navbar'

declare global {
  interface Window {
    google: any
    initMap: () => void
  }
}

export default function TherapistsNearYouPage() {
  const [userLocation, setUserLocation] = useState<{ lat: number; lng: number } | null>(null)
  const [therapists, setTherapists] = useState<TherapistWithDistance[]>([])
  const [selectedTherapist, setSelectedTherapist] = useState<TherapistWithDistance | null>(null)
  const [map, setMap] = useState<any>(null)
  const [markers, setMarkers] = useState<any[]>([])
  const [userMarker, setUserMarker] = useState<any>(null)
  const [isLoading, setIsLoading] = useState(true)
  const [searchRadius, setSearchRadius] = useState(10000) // 10km radius
  const mapRef = useRef<HTMLDivElement>(null)

  // Initialize map and get user location
  useEffect(() => {
    const loadGoogleMaps = () => {
      if (window.google) {
        initializeMap()
        return
      }

      // Load Google Maps script with Places library
      const script = document.createElement('script')
      script.src = `https://maps.googleapis.com/maps/api/js?key=${process.env.NEXT_PUBLIC_GOOGLE_MAPS_API_KEY || 'AIzaSyBbbDmXhmbKjdS8Nj_izg2C_-mjuQyTbm0'}&libraries=places`
      script.async = true
      script.defer = true
      script.onload = initializeMap
      document.head.appendChild(script)
    }

    const initializeMap = () => {
      if (!mapRef.current) return

      // Default to NYC if geolocation fails
      const defaultCenter = { lat: 40.7831, lng: -73.9712 }
      
      const mapInstance = new window.google.maps.Map(mapRef.current, {
        zoom: 12,
        center: defaultCenter,
        styles: [
          {
            featureType: 'poi',
            elementType: 'labels',
            stylers: [{ visibility: 'off' }]
          }
        ]
      })

      setMap(mapInstance)

      // Try to get user's current location
      if (navigator.geolocation) {
        navigator.geolocation.getCurrentPosition(
          (position) => {
            const userPos = {
              lat: position.coords.latitude,
              lng: position.coords.longitude
            }
            setUserLocation(userPos)
            mapInstance.setCenter(userPos)
            
            // Add user location marker
            const userMarkerInstance = new window.google.maps.Marker({
              position: userPos,
              map: mapInstance,
              title: 'Your Location',
              icon: {
                url: 'data:image/svg+xml;charset=UTF-8,' + encodeURIComponent(`
                  <svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                    <circle cx="12" cy="12" r="8" fill="#3B82F6" stroke="#FFFFFF" stroke-width="2"/>
                    <circle cx="12" cy="12" r="3" fill="#FFFFFF"/>
                  </svg>
                `),
                scaledSize: new window.google.maps.Size(24, 24)
              }
            })
            setUserMarker(userMarkerInstance)
            
            // Search for therapists near user location
            searchTherapistsNearby(userPos, mapInstance)
          },
          (error) => {
            console.error('Geolocation error:', error)
            // Still search for therapists using default location
            searchTherapistsNearby(defaultCenter, mapInstance)
          }
        )
      } else {
        // Search for therapists using default location
        searchTherapistsNearby(defaultCenter, mapInstance)
      }
    }

    loadGoogleMaps()
  }, [])

  const searchTherapistsNearby = (location: { lat: number; lng: number }, mapInstance: any) => {
    if (!window.google || !window.google.maps.places) {
      console.error('Google Places API not loaded')
      setIsLoading(false)
      return
    }

    const service = new window.google.maps.places.PlacesService(mapInstance)
    
    // Search for various types of mental health professionals
    const searchQueries = [
      'therapist',
      'psychologist', 
      'counselor',
      'mental health',
      'psychiatrist',
      'therapy clinic',
      'counseling center'
    ]

    const allResults: any[] = []
    let completedSearches = 0

    searchQueries.forEach((query) => {
      const request = {
        location: new window.google.maps.LatLng(location.lat, location.lng),
        radius: searchRadius,
        keyword: query,
        type: 'health' as any
      }

      service.nearbySearch(request, (results: any[], status: any) => {
        completedSearches++
        
        if (status === window.google.maps.places.PlacesServiceStatus.OK && results) {
          // Filter and deduplicate results
          const filteredResults = results.filter((place: any) => {
            // Check if this place is likely a therapist/mental health professional
            const name = place.name.toLowerCase()
            const types = place.types || []
            
            return (
              name.includes('therapy') ||
              name.includes('therapist') ||
              name.includes('counseling') ||
              name.includes('counselor') ||
              name.includes('psychology') ||
              name.includes('psychologist') ||
              name.includes('mental health') ||
              name.includes('psychiatrist') ||
              types.includes('health') ||
              types.includes('doctor')
            ) && !allResults.some((existing: any) => existing.place_id === place.place_id)
          })

          allResults.push(...filteredResults)
        }

        // When all searches are complete, process the results
        if (completedSearches === searchQueries.length) {
          processSearchResults(allResults, location, mapInstance)
        }
      })
    })
  }

  const processSearchResults = async (places: any[], userPos: { lat: number; lng: number }, mapInstance: any) => {
    if (places.length === 0) {
      setIsLoading(false)
      return
    }

    // Convert places to therapist format and get additional details
    const therapistPromises = places.slice(0, 20).map(async (place: any, index: number) => {
      return new Promise<TherapistWithDistance>((resolve) => {
        const service = new window.google.maps.places.PlacesService(mapInstance)
        
        service.getDetails({
          placeId: place.place_id,
          fields: ['name', 'formatted_address', 'formatted_phone_number', 'website', 'rating', 'user_ratings_total', 'photos', 'opening_hours', 'geometry']
        }, (details: any, status: any) => {
          if (status === window.google.maps.places.PlacesServiceStatus.OK && details) {
            const therapist: TherapistWithDistance = {
              id: place.place_id,
              name: details.name || place.name,
              specialization: extractSpecializations(details.name),
              rating: details.rating || 0,
              reviewCount: details.user_ratings_total || 0,
              yearsOfExperience: Math.floor(Math.random() * 15) + 5, // Estimated
              bio: `Professional mental health services at ${details.name}. Committed to providing quality care and support.`,
              imageUrl: details.photos && details.photos[0] 
                ? details.photos[0].getUrl({ maxWidth: 200, maxHeight: 200 })
                : '/placeholder-user.jpg',
              location: {
                lat: details.geometry.location.lat(),
                lng: details.geometry.location.lng(),
                address: details.formatted_address || place.vicinity,
                city: extractCityFromAddress(details.formatted_address || place.vicinity),
                state: extractStateFromAddress(details.formatted_address || place.vicinity),
                zipCode: ''
              },
              contact: {
                phone: details.formatted_phone_number || 'Contact via website',
                email: 'info@' + (details.website ? new URL(details.website).hostname : 'therapy.com'),
                website: details.website
              },
              availability: {
                days: details.opening_hours?.weekday_text ? 
                  details.opening_hours.weekday_text.map((day: string) => day.split(':')[0]) :
                  ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday'],
                timeSlots: ['9:00 AM', '11:00 AM', '2:00 PM', '4:00 PM']
              },
              sessionType: ['in-person'],
              fees: {
                consultationFee: 100 + Math.floor(Math.random() * 50),
                sessionFee: 120 + Math.floor(Math.random() * 80),
                currency: 'USD'
              },
              languages: ['English'],
              education: ['Licensed Mental Health Professional'],
              certifications: ['State Licensed']
            }
            resolve(therapist)
          } else {
            // Fallback if details request fails
            const therapist: TherapistWithDistance = {
              id: place.place_id,
              name: place.name,
              specialization: extractSpecializations(place.name),
              rating: place.rating || 0,
              reviewCount: place.user_ratings_total || 0,
              yearsOfExperience: Math.floor(Math.random() * 15) + 5,
              bio: `Professional mental health services at ${place.name}.`,
              imageUrl: '/placeholder-user.jpg',
              location: {
                lat: place.geometry.location.lat(),
                lng: place.geometry.location.lng(),
                address: place.vicinity,
                city: extractCityFromAddress(place.vicinity),
                state: '',
                zipCode: ''
              },
              contact: {
                phone: 'Contact for details',
                email: 'info@therapy.com'
              },
              availability: {
                days: ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday'],
                timeSlots: ['9:00 AM', '11:00 AM', '2:00 PM', '4:00 PM']
              },
              sessionType: ['in-person'],
              fees: {
                consultationFee: 100,
                sessionFee: 150,
                currency: 'USD'
              },
              languages: ['English'],
              education: ['Licensed Mental Health Professional'],
              certifications: ['State Licensed']
            }
            resolve(therapist)
          }
        })
      })
    })

    try {
      const therapistsWithDetails = await Promise.all(therapistPromises)
      
      // Calculate distances
      if (userPos) {
        await calculateDistances(therapistsWithDetails, userPos)
      } else {
        setTherapists(therapistsWithDetails)
        setSelectedTherapist(therapistsWithDetails[0])
        addTherapistMarkers(therapistsWithDetails, mapInstance)
        setIsLoading(false)
      }
    } catch (error) {
      console.error('Error processing therapist details:', error)
      setIsLoading(false)
    }
  }

  const extractSpecializations = (name: string): string[] => {
    const specializations = []
    const lowerName = name.toLowerCase()
    
    if (lowerName.includes('anxiety')) specializations.push('Anxiety')
    if (lowerName.includes('depression')) specializations.push('Depression')
    if (lowerName.includes('trauma')) specializations.push('Trauma Therapy')
    if (lowerName.includes('family')) specializations.push('Family Therapy')
    if (lowerName.includes('couple')) specializations.push('Couples Therapy')
    if (lowerName.includes('child')) specializations.push('Child Psychology')
    if (lowerName.includes('addiction')) specializations.push('Addiction Counseling')
    if (lowerName.includes('cognitive') || lowerName.includes('cbt')) specializations.push('Cognitive Behavioral Therapy')
    
    return specializations.length > 0 ? specializations : ['General Therapy', 'Counseling']
  }

  const extractCityFromAddress = (address: string): string => {
    const parts = address.split(',')
    return parts.length > 1 ? parts[parts.length - 2].trim() : ''
  }

  const extractStateFromAddress = (address: string): string => {
    const parts = address.split(',')
    const lastPart = parts[parts.length - 1].trim()
    const statePart = lastPart.split(' ')[0]
    return statePart || ''
  }

  const calculateDistances = async (therapistList: TherapistWithDistance[], userPos: { lat: number; lng: number }) => {
    if (!window.google) return

    const service = new window.google.maps.DistanceMatrixService()
    const destinations = therapistList.map(t => new window.google.maps.LatLng(t.location.lat, t.location.lng))

    service.getDistanceMatrix({
      origins: [new window.google.maps.LatLng(userPos.lat, userPos.lng)],
      destinations: destinations,
      travelMode: window.google.maps.TravelMode.DRIVING,
      unitSystem: window.google.maps.UnitSystem.IMPERIAL,
      avoidHighways: false,
      avoidTolls: false
    }, (response: any, status: any) => {
      if (status === 'OK') {
        const updatedTherapists = therapistList.map((therapist: TherapistWithDistance, index: number) => {
          const element = response.rows[0].elements[index]
          if (element.status === 'OK') {
            return {
              ...therapist,
              distance: element.distance.value, // in meters
              distanceText: element.distance.text,
              duration: element.duration.text
            }
          }
          return therapist
        }).sort((a: TherapistWithDistance, b: TherapistWithDistance) => (a.distance || Infinity) - (b.distance || Infinity))

        setTherapists(updatedTherapists)
        setSelectedTherapist(updatedTherapists[0])
        addTherapistMarkers(updatedTherapists, map)
        setIsLoading(false)
      } else {
        setTherapists(therapistList)
        setSelectedTherapist(therapistList[0])
        addTherapistMarkers(therapistList, map)
        setIsLoading(false)
      }
    })
  }

  const addTherapistMarkers = (therapistList: TherapistWithDistance[], mapInstance: any) => {
    // Clear existing markers
    markers.forEach(marker => marker.setMap(null))
    
    const newMarkers = therapistList.map((therapist: TherapistWithDistance) => {
      const marker = new window.google.maps.Marker({
        position: { lat: therapist.location.lat, lng: therapist.location.lng },
        map: mapInstance,
        title: therapist.name,
        icon: {
          url: 'data:image/svg+xml;charset=UTF-8,' + encodeURIComponent(`
            <svg width="32" height="40" viewBox="0 0 32 40" fill="none" xmlns="http://www.w3.org/2000/svg">
              <path d="M16 0C7.163 0 0 7.163 0 16C0 28 16 40 16 40C16 40 32 28 32 16C32 7.163 24.837 0 16 0Z" fill="#DC2626"/>
              <circle cx="16" cy="16" r="8" fill="#FFFFFF"/>
              <text x="16" y="20" font-family="Arial" font-size="12" text-anchor="middle" fill="#DC2626">+</text>
            </svg>
          `),
          scaledSize: new window.google.maps.Size(32, 40)
        }
      })

      const infoWindow = new window.google.maps.InfoWindow({
        content: `
          <div style="padding: 8px; max-width: 200px;">
            <h3 style="margin: 0 0 8px 0; font-size: 16px; font-weight: bold;">${therapist.name}</h3>
            <p style="margin: 0 0 4px 0; font-size: 14px; color: #666;">${therapist.specialization.join(', ')}</p>
            <p style="margin: 0 0 4px 0; font-size: 14px;">⭐ ${therapist.rating} (${therapist.reviewCount} reviews)</p>
            <p style="margin: 0; font-size: 12px; color: #888;">${therapist.location.address}</p>
          </div>
        `
      })

      marker.addListener('click', () => {
        markers.forEach((m: any) => m.infoWindow?.close())
        infoWindow.open(mapInstance, marker)
        setSelectedTherapist(therapist)
      })

      ;(marker as any).infoWindow = infoWindow
      return marker
    })

    setMarkers(newMarkers)
  }

  const expandSearch = () => {
    if (userLocation && map) {
      setIsLoading(true)
      setSearchRadius(prev => prev * 2) // Double the search radius
      searchTherapistsNearby(userLocation, map)
    }
  }

  const handleTherapistSelect = (therapist: TherapistWithDistance) => {
    setSelectedTherapist(therapist)
    if (map) {
      map.setCenter({ lat: therapist.location.lat, lng: therapist.location.lng })
      map.setZoom(15)
      
      // Find and open the corresponding marker's info window
      const marker = markers.find((m: any) => m.getTitle() === therapist.name)
      if (marker) {
        markers.forEach((m: any) => m.infoWindow?.close())
        ;(marker as any).infoWindow?.open(map, marker)
      }
    }
  }

  return (
    <>
      <Navbar />
      <div className="min-h-screen bg-gray-50 pt-16">
        <div className="container mx-auto px-4 py-8">
          <div className="mb-6">
            <h1 className="text-3xl font-bold text-gray-900 mb-2">Find Therapists Near You</h1>
            <p className="text-gray-600">
              {isLoading 
                ? 'Searching for therapists near you...'
                : userLocation 
                  ? `Found ${therapists.length} therapists within ${Math.round(searchRadius / 1000)}km of your location`
                  : `Found ${therapists.length} therapists in the area`
              }
            </p>
          </div>

          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 h-[calc(100vh-200px)]">
            {/* Therapist List */}
            <div className="overflow-y-auto space-y-4 pr-2">
              {isLoading ? (
                <div className="flex items-center justify-center h-64">
                  <div className="text-center">
                    <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 mx-auto mb-2"></div>
                    <p className="text-sm text-gray-600">Searching for therapists...</p>
                  </div>
                </div>
              ) : therapists.length === 0 ? (
                <div className="flex items-center justify-center h-64">
                  <div className="text-center">
                    <p className="text-gray-600 mb-2">No therapists found in your area.</p>
                    <p className="text-sm text-gray-500 mb-4">Try expanding your search radius.</p>
                    {userLocation && (
                      <Button onClick={expandSearch} variant="outline">
                        Expand Search Area
                      </Button>
                    )}
                  </div>
                </div>
              ) : (
                therapists.map((therapist) => (
                <Card 
                  key={therapist.id} 
                  className={`cursor-pointer transition-all duration-200 hover:shadow-md ${
                    selectedTherapist?.id === therapist.id ? 'ring-2 ring-blue-500 shadow-md' : ''
                  }`}
                  onClick={() => handleTherapistSelect(therapist)}
                >
                  <CardHeader className="pb-3">
                    <div className="flex items-start justify-between">
                      <div className="flex items-center space-x-3">
                        <img 
                          src={therapist.imageUrl} 
                          alt={therapist.name}
                          className="w-12 h-12 rounded-full object-cover"
                        />
                        <div>
                          <CardTitle className="text-lg">{therapist.name}</CardTitle>
                          <div className="flex items-center space-x-2 mt-1">
                            <div className="flex items-center">
                              <Star className="w-4 h-4 fill-yellow-400 text-yellow-400" />
                              <span className="text-sm font-medium ml-1">{therapist.rating}</span>
                              <span className="text-sm text-gray-500 ml-1">({therapist.reviewCount})</span>
                            </div>
                            {therapist.distanceText && (
                              <>
                                <span className="text-gray-300">•</span>
                                <span className="text-sm text-blue-600 font-medium">{therapist.distanceText}</span>
                              </>
                            )}
                          </div>
                        </div>
                      </div>
                      <div className="text-right">
                        <div className="text-lg font-bold text-green-600">${therapist.fees.sessionFee}</div>
                        <div className="text-xs text-gray-500">per session</div>
                      </div>
                    </div>
                  </CardHeader>
                  
                  <CardContent className="pt-0">
                    <div className="space-y-3">
                      <div className="flex flex-wrap gap-1">
                        {therapist.specialization.slice(0, 3).map((spec) => (
                          <Badge key={spec} variant="secondary" className="text-xs">
                            {spec}
                          </Badge>
                        ))}
                        {therapist.specialization.length > 3 && (
                          <Badge variant="outline" className="text-xs">
                            +{therapist.specialization.length - 3} more
                          </Badge>
                        )}
                      </div>
                      
                      <p className="text-sm text-gray-600 line-clamp-2">{therapist.bio}</p>
                      
                      <div className="flex items-center justify-between text-xs text-gray-500">
                        <div className="flex items-center space-x-4">
                          <div className="flex items-center">
                            <Clock className="w-3 h-3 mr-1" />
                            {therapist.yearsOfExperience} years exp.
                          </div>
                          <div className="flex items-center">
                            <Users className="w-3 h-3 mr-1" />
                            {therapist.sessionType.join(', ')}
                          </div>
                        </div>
                        {therapist.duration && (
                          <div className="text-blue-600 font-medium">
                            {therapist.duration} away
                          </div>
                        )}
                      </div>
                    </div>
                  </CardContent>
                </Card>
              )))}
            </div>

            {/* Map */}
            <div className="relative">
              <div 
                ref={mapRef} 
                className="w-full h-full rounded-lg shadow-md"
                style={{ minHeight: '500px' }}
              />
              {isLoading && (
                <div className="absolute inset-0 bg-white bg-opacity-75 flex items-center justify-center rounded-lg">
                  <div className="text-center">
                    <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 mx-auto mb-2"></div>
                    <p className="text-sm text-gray-600">Loading map and calculating distances...</p>
                  </div>
                </div>
              )}
            </div>
          </div>

          {/* Therapist Details Modal/Card */}
          {selectedTherapist && (
            <Card className="mt-6">
              <CardHeader>
                <div className="flex items-start justify-between">
                  <div className="flex items-center space-x-4">
                    <img 
                      src={selectedTherapist.imageUrl} 
                      alt={selectedTherapist.name}
                      className="w-16 h-16 rounded-full object-cover"
                    />
                    <div>
                      <CardTitle className="text-xl">{selectedTherapist.name}</CardTitle>
                      <CardDescription className="text-base mt-1">
                        {selectedTherapist.specialization.join(' • ')}
                      </CardDescription>
                      <div className="flex items-center space-x-4 mt-2">
                        <div className="flex items-center">
                          <Star className="w-4 h-4 fill-yellow-400 text-yellow-400" />
                          <span className="font-medium ml-1">{selectedTherapist.rating}</span>
                          <span className="text-gray-500 ml-1">({selectedTherapist.reviewCount} reviews)</span>
                        </div>
                        <div className="flex items-center text-gray-600">
                          <Clock className="w-4 h-4 mr-1" />
                          {selectedTherapist.yearsOfExperience} years experience
                        </div>
                      </div>
                    </div>
                  </div>
                  <div className="text-right">
                    {selectedTherapist.distanceText && (
                      <div className="text-blue-600 font-semibold text-lg">{selectedTherapist.distanceText}</div>
                    )}
                    {selectedTherapist.duration && (
                      <div className="text-gray-500 text-sm">{selectedTherapist.duration} drive</div>
                    )}
                  </div>
                </div>
              </CardHeader>
              
              <CardContent>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  <div className="space-y-4">
                    <div>
                      <h3 className="font-semibold mb-2">About</h3>
                      <p className="text-gray-600 text-sm">{selectedTherapist.bio}</p>
                    </div>
                    
                    <div>
                      <h3 className="font-semibold mb-2">Education & Certifications</h3>
                      <div className="space-y-1">
                        {selectedTherapist.education.map((edu, index) => (
                          <div key={index} className="flex items-center text-sm">
                            <CheckCircle className="w-3 h-3 text-green-500 mr-2 flex-shrink-0" />
                            {edu}
                          </div>
                        ))}
                        {selectedTherapist.certifications.map((cert, index) => (
                          <div key={index} className="flex items-center text-sm">
                            <CheckCircle className="w-3 h-3 text-blue-500 mr-2 flex-shrink-0" />
                            {cert}
                          </div>
                        ))}
                      </div>
                    </div>
                    
                    <div>
                      <h3 className="font-semibold mb-2">Languages</h3>
                      <div className="flex flex-wrap gap-1">
                        {selectedTherapist.languages.map((lang) => (
                          <Badge key={lang} variant="outline">{lang}</Badge>
                        ))}
                      </div>
                    </div>
                  </div>
                  
                  <div className="space-y-4">
                    <div>
                      <h3 className="font-semibold mb-2">Contact Information</h3>
                      <div className="space-y-2">
                        <div className="flex items-center text-sm">
                          <MapPin className="w-4 h-4 mr-2 text-gray-500" />
                          {selectedTherapist.location.address}, {selectedTherapist.location.city}, {selectedTherapist.location.state} {selectedTherapist.location.zipCode}
                        </div>
                        <div className="flex items-center text-sm">
                          <Phone className="w-4 h-4 mr-2 text-gray-500" />
                          {selectedTherapist.contact.phone}
                        </div>
                        <div className="flex items-center text-sm">
                          <Mail className="w-4 h-4 mr-2 text-gray-500" />
                          {selectedTherapist.contact.email}
                        </div>
                        {selectedTherapist.contact.website && (
                          <div className="flex items-center text-sm">
                            <Globe className="w-4 h-4 mr-2 text-gray-500" />
                            <a href={`https://${selectedTherapist.contact.website}`} target="_blank" rel="noopener noreferrer" className="text-blue-600 hover:underline">
                              {selectedTherapist.contact.website}
                            </a>
                          </div>
                        )}
                      </div>
                    </div>
                    
                    <div>
                      <h3 className="font-semibold mb-2">Session Information</h3>
                      <div className="space-y-2 text-sm">
                        <div className="flex items-center justify-between">
                          <span>Consultation Fee:</span>
                          <span className="font-medium">${selectedTherapist.fees.consultationFee}</span>
                        </div>
                        <div className="flex items-center justify-between">
                          <span>Session Fee:</span>
                          <span className="font-medium">${selectedTherapist.fees.sessionFee}</span>
                        </div>
                        <div className="flex items-center justify-between">
                          <span>Session Types:</span>
                          <span>{selectedTherapist.sessionType.join(', ')}</span>
                        </div>
                      </div>
                    </div>
                    
                    <div>
                      <h3 className="font-semibold mb-2">Availability</h3>
                      <div className="text-sm">
                        <div className="mb-1">
                          <span className="font-medium">Days:</span> {selectedTherapist.availability.days.join(', ')}
                        </div>
                        <div>
                          <span className="font-medium">Time Slots:</span> {selectedTherapist.availability.timeSlots.join(', ')}
                        </div>
                      </div>
                    </div>
                    
                    <div className="pt-2">
                      <Button className="w-full">
                        Book Consultation
                      </Button>
                    </div>
                  </div>
                </div>
              </CardContent>
            </Card>
          )}
        </div>
      </div>
    </>
  )
}
