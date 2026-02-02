/**
 * Smart Campus Attendance Management System
 * JavaScript functionality for attendance operations
 */

// CSRF Token handling
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

const csrftoken = getCookie('csrftoken');

// Configure jQuery AJAX
$.ajaxSetup({
    beforeSend: function(xhr, settings) {
        if (!(/^http:.*/.test(settings.url) || /^https:.*/.test(settings.url))) {
            xhr.setRequestHeader("X-CSRFToken", csrftoken);
        }
    }
});

/**
 * Attendance Manager Class
 */
class AttendanceManager {
    constructor(sessionId) {
        this.sessionId = sessionId;
        this.stats = {
            total: 0,
            present: 0,
            absent: 0,
            late: 0
        };
        this.autoRefreshInterval = null;
    }

    /**
     * Update attendance status via AJAX
     */
    updateStatus(attendanceId, newStatus, callback) {
        $.ajax({
            url: '/attendance/ajax/update-attendance/',
            method: 'POST',
            data: {
                attendance_id: attendanceId,
                status: newStatus
            },
            success: (response) => {
                if (response.success) {
                    this.refreshStats();
                    if (callback) callback(response);
                    this.showNotification('Attendance updated successfully', 'success');
                }
            },
            error: (xhr) => {
                this.showNotification('Failed to update attendance', 'error');
            }
        });
    }

    /**
     * Refresh session statistics
     */
    refreshStats() {
        if (!this.sessionId) return;

        $.ajax({
            url: `/attendance/ajax/session-stats/${this.sessionId}/`,
            method: 'GET',
            success: (response) => {
                this.stats = response;
                this.updateStatsDisplay();
            }
        });
    }

    /**
     * Update statistics display
     */
    updateStatsDisplay() {
        $('#total-count').text(this.stats.total);
        $('#present-count').text(this.stats.present);
        $('#absent-count').text(this.stats.absent);
        $('#late-count').text(this.stats.late);

        // Update percentage if element exists
        if (this.stats.total > 0) {
            const percentage = ((this.stats.present + this.stats.late) / this.stats.total * 100).toFixed(1);
            $('#attendance-percentage').text(percentage + '%');
        }
    }

    /**
     * Start auto-refresh
     */
    startAutoRefresh(interval = 5000) {
        this.autoRefreshInterval = setInterval(() => {
            this.refreshStats();
        }, interval);
    }

    /**
     * Stop auto-refresh
     */
    stopAutoRefresh() {
        if (this.autoRefreshInterval) {
            clearInterval(this.autoRefreshInterval);
            this.autoRefreshInterval = null;
        }
    }

    /**
     * Show notification
     */
    showNotification(message, type = 'info') {
        const alertClass = {
            'success': 'alert-success',
            'error': 'alert-danger',
            'warning': 'alert-warning',
            'info': 'alert-info'
        }[type] || 'alert-info';

        const notification = $(`
            <div class="alert ${alertClass} alert-dismissible fade show notification-toast" role="alert">
                ${message}
                <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
            </div>
        `);

        // Add to notification container or body
        let container = $('#notification-container');
        if (!container.length) {
            container = $('<div id="notification-container" style="position: fixed; top: 20px; right: 20px; z-index: 9999;"></div>');
            $('body').append(container);
        }

        container.append(notification);

        // Auto-dismiss after 3 seconds
        setTimeout(() => {
            notification.alert('close');
        }, 3000);
    }
}

/**
 * Face Recognition Manager Class
 */
class FaceRecognitionManager {
    constructor(sessionId) {
        this.sessionId = sessionId;
        this.video = null;
        this.canvas = null;
        this.stream = null;
        this.autoMode = false;
        this.autoInterval = null;
        this.recognizedStudents = new Set();
    }

    /**
     * Initialize camera
     */
    async initCamera(videoElement, canvasElement) {
        this.video = videoElement;
        this.canvas = canvasElement;

        try {
            this.stream = await navigator.mediaDevices.getUserMedia({
                video: { width: 640, height: 480, facingMode: 'user' }
            });
            this.video.srcObject = this.stream;
            return true;
        } catch (err) {
            console.error('Camera access error:', err);
            return false;
        }
    }

    /**
     * Stop camera
     */
    stopCamera() {
        if (this.stream) {
            this.stream.getTracks().forEach(track => track.stop());
            this.video.srcObject = null;
        }
        this.stopAutoMode();
    }

    /**
     * Capture frame and send for recognition
     */
    async captureAndRecognize() {
        if (!this.video || !this.canvas) return;

        const ctx = this.canvas.getContext('2d');
        this.canvas.width = this.video.videoWidth;
        this.canvas.height = this.video.videoHeight;
        ctx.drawImage(this.video, 0, 0);

        // Convert to blob
        return new Promise((resolve) => {
            this.canvas.toBlob(async (blob) => {
                const formData = new FormData();
                formData.append('image', blob, 'capture.jpg');
                formData.append('session_id', this.sessionId);

                try {
                    const response = await fetch('/face-recognition/process/', {
                        method: 'POST',
                        headers: {
                            'X-CSRFToken': csrftoken
                        },
                        body: formData
                    });

                    const result = await response.json();
                    resolve(result);
                } catch (err) {
                    console.error('Recognition error:', err);
                    resolve({ success: false, error: err.message });
                }
            }, 'image/jpeg', 0.9);
        });
    }

    /**
     * Start auto recognition mode
     */
    startAutoMode(interval = 3000) {
        this.autoMode = true;
        this.autoInterval = setInterval(async () => {
            const result = await this.captureAndRecognize();
            if (result.success && result.recognized) {
                this.onStudentRecognized(result);
            }
        }, interval);
    }

    /**
     * Stop auto recognition mode
     */
    stopAutoMode() {
        this.autoMode = false;
        if (this.autoInterval) {
            clearInterval(this.autoInterval);
            this.autoInterval = null;
        }
    }

    /**
     * Handle recognized student
     */
    onStudentRecognized(result) {
        if (this.recognizedStudents.has(result.student.id)) return;

        this.recognizedStudents.add(result.student.id);

        // Trigger custom event
        const event = new CustomEvent('studentRecognized', {
            detail: {
                student: result.student,
                confidence: result.confidence
            }
        });
        document.dispatchEvent(event);
    }
}

/**
 * Notification Manager Class
 */
class NotificationManager {
    constructor() {
        this.unreadCount = 0;
        this.pollInterval = null;
    }

    /**
     * Start polling for new notifications
     */
    startPolling(interval = 30000) {
        this.checkUnread();
        this.pollInterval = setInterval(() => {
            this.checkUnread();
        }, interval);
    }

    /**
     * Stop polling
     */
    stopPolling() {
        if (this.pollInterval) {
            clearInterval(this.pollInterval);
            this.pollInterval = null;
        }
    }

    /**
     * Check for unread notifications
     */
    checkUnread() {
        $.ajax({
            url: '/notifications/unread-count/',
            method: 'GET',
            success: (response) => {
                this.unreadCount = response.count;
                this.updateBadge();
            }
        });
    }

    /**
     * Update notification badge
     */
    updateBadge() {
        const badge = $('#notification-badge');
        if (this.unreadCount > 0) {
            badge.text(this.unreadCount).show();
        } else {
            badge.hide();
        }
    }

    /**
     * Mark notification as read
     */
    markAsRead(notificationId) {
        $.ajax({
            url: `/notifications/${notificationId}/mark-read/`,
            method: 'POST',
            success: () => {
                this.checkUnread();
            }
        });
    }

    /**
     * Mark all as read
     */
    markAllAsRead() {
        $.ajax({
            url: '/notifications/mark-all-read/',
            method: 'POST',
            success: () => {
                this.unreadCount = 0;
                this.updateBadge();
            }
        });
    }
}

// Export for use in templates
window.AttendanceManager = AttendanceManager;
window.FaceRecognitionManager = FaceRecognitionManager;
window.NotificationManager = NotificationManager;

// Initialize notification polling on page load
$(document).ready(function() {
    const notificationManager = new NotificationManager();
    notificationManager.startPolling();
});
