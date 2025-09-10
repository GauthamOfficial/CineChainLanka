/**
 * Service Worker for CineChainLanka PWA
 * Provides offline functionality and caching
 */

const CACHE_NAME = 'cinechain-v1';
const STATIC_CACHE = 'cinechain-static-v1';
const DYNAMIC_CACHE = 'cinechain-dynamic-v1';
const API_CACHE = 'cinechain-api-v1';

// Files to cache for offline functionality
const STATIC_FILES = [
    '/',
    '/static/css/main.css',
    '/static/js/main.js',
    '/static/media/logo.svg',
    '/manifest.json',
    '/offline.html'
];

// API endpoints to cache
const API_ENDPOINTS = [
    '/api/campaigns/',
    '/api/users/profile/',
    '/api/analytics/creator/',
    '/api/marketplace/listings/'
];

// Install event - cache static files
self.addEventListener('install', (event) => {
    console.log('Service Worker installing...');
    event.waitUntil(
        caches.open(STATIC_CACHE)
            .then((cache) => {
                console.log('Caching static files');
                return cache.addAll(STATIC_FILES);
            })
            .then(() => {
                console.log('Static files cached successfully');
                return self.skipWaiting();
            })
            .catch((error) => {
                console.error('Failed to cache static files:', error);
            })
    );
});

// Activate event - clean up old caches
self.addEventListener('activate', (event) => {
    console.log('Service Worker activating...');
    event.waitUntil(
        caches.keys()
            .then((cacheNames) => {
                return Promise.all(
                    cacheNames.map((cacheName) => {
                        if (cacheName !== STATIC_CACHE && 
                            cacheName !== DYNAMIC_CACHE && 
                            cacheName !== API_CACHE) {
                            console.log('Deleting old cache:', cacheName);
                            return caches.delete(cacheName);
                        }
                    })
                );
            })
            .then(() => {
                console.log('Service Worker activated');
                return self.clients.claim();
            })
    );
});

// Fetch event - serve from cache or network
self.addEventListener('fetch', (event) => {
    const { request } = event;
    const url = new URL(request.url);

    // Handle different types of requests
    if (request.method === 'GET') {
        if (isStaticFile(request.url)) {
            event.respondWith(handleStaticFile(request));
        } else if (isAPIRequest(request.url)) {
            event.respondWith(handleAPIRequest(request));
        } else if (isPageRequest(request)) {
            event.respondWith(handlePageRequest(request));
        } else {
            event.respondWith(handleOtherRequest(request));
        }
    } else {
        // For non-GET requests, try network first
        event.respondWith(fetch(request));
    }
});

// Check if request is for a static file
function isStaticFile(url) {
    return url.includes('/static/') || 
           url.includes('/media/') || 
           url.endsWith('.css') || 
           url.endsWith('.js') || 
           url.endsWith('.png') || 
           url.endsWith('.jpg') || 
           url.endsWith('.svg');
}

// Check if request is for an API endpoint
function isAPIRequest(url) {
    return url.includes('/api/');
}

// Check if request is for a page
function isPageRequest(request) {
    return request.headers.get('accept').includes('text/html');
}

// Handle static file requests
async function handleStaticFile(request) {
    try {
        const cache = await caches.open(STATIC_CACHE);
        const cachedResponse = await cache.match(request);
        
        if (cachedResponse) {
            return cachedResponse;
        }
        
        const networkResponse = await fetch(request);
        if (networkResponse.ok) {
            cache.put(request, networkResponse.clone());
        }
        return networkResponse;
    } catch (error) {
        console.error('Error handling static file:', error);
        return new Response('Static file not available offline', { status: 404 });
    }
}

// Handle API requests
async function handleAPIRequest(request) {
    try {
        const cache = await caches.open(API_CACHE);
        const cachedResponse = await cache.match(request);
        
        // Try network first for API requests
        try {
            const networkResponse = await fetch(request);
            if (networkResponse.ok) {
                // Cache successful API responses
                cache.put(request, networkResponse.clone());
            }
            return networkResponse;
        } catch (networkError) {
            // If network fails, try to serve from cache
            if (cachedResponse) {
                console.log('Serving API response from cache:', request.url);
                return cachedResponse;
            }
            throw networkError;
        }
    } catch (error) {
        console.error('Error handling API request:', error);
        return new Response(JSON.stringify({
            error: 'API not available offline',
            message: 'Please check your internet connection'
        }), {
            status: 503,
            headers: { 'Content-Type': 'application/json' }
        });
    }
}

// Handle page requests
async function handlePageRequest(request) {
    try {
        const cache = await caches.open(DYNAMIC_CACHE);
        const cachedResponse = await cache.match(request);
        
        // Try network first
        try {
            const networkResponse = await fetch(request);
            if (networkResponse.ok) {
                cache.put(request, networkResponse.clone());
            }
            return networkResponse;
        } catch (networkError) {
            // If network fails, try to serve from cache
            if (cachedResponse) {
                console.log('Serving page from cache:', request.url);
                return cachedResponse;
            }
            
            // If no cached version, serve offline page
            return caches.match('/offline.html');
        }
    } catch (error) {
        console.error('Error handling page request:', error);
        return caches.match('/offline.html');
    }
}

// Handle other requests
async function handleOtherRequest(request) {
    try {
        return await fetch(request);
    } catch (error) {
        console.error('Error handling other request:', error);
        return new Response('Request failed', { status: 503 });
    }
}

// Background sync for offline actions
self.addEventListener('sync', (event) => {
    console.log('Background sync triggered:', event.tag);
    
    if (event.tag === 'offline-actions') {
        event.waitUntil(handleOfflineActions());
    }
});

// Handle offline actions when back online
async function handleOfflineActions() {
    try {
        // Get offline actions from IndexedDB
        const offlineActions = await getOfflineActions();
        
        for (const action of offlineActions) {
            try {
                await fetch(action.url, {
                    method: action.method,
                    headers: action.headers,
                    body: action.body
                });
                
                // Remove successful action
                await removeOfflineAction(action.id);
                console.log('Offline action synced:', action.url);
            } catch (error) {
                console.error('Failed to sync offline action:', error);
            }
        }
    } catch (error) {
        console.error('Error handling offline actions:', error);
    }
}

// Push notification handling
self.addEventListener('push', (event) => {
    console.log('Push notification received:', event);
    
    const options = {
        body: event.data ? event.data.text() : 'New notification from CineChainLanka',
        icon: '/logo192.png',
        badge: '/logo192.png',
        vibrate: [100, 50, 100],
        data: {
            dateOfArrival: Date.now(),
            primaryKey: 1
        },
        actions: [
            {
                action: 'explore',
                title: 'View Details',
                icon: '/logo192.png'
            },
            {
                action: 'close',
                title: 'Close',
                icon: '/logo192.png'
            }
        ]
    };
    
    event.waitUntil(
        self.registration.showNotification('CineChainLanka', options)
    );
});

// Notification click handling
self.addEventListener('notificationclick', (event) => {
    console.log('Notification clicked:', event);
    
    event.notification.close();
    
    if (event.action === 'explore') {
        event.waitUntil(
            clients.openWindow('/')
        );
    }
});

// Helper functions for offline actions (simplified)
async function getOfflineActions() {
    // In a real implementation, this would read from IndexedDB
    return [];
}

async function removeOfflineAction(actionId) {
    // In a real implementation, this would remove from IndexedDB
    console.log('Removing offline action:', actionId);
}

