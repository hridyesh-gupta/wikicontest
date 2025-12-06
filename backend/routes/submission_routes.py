"""
Submission Routes for WikiContest Application
Handles submission management and review functionality
"""

from flask import Blueprint, request, jsonify

from database import db
from middleware.auth import require_auth, require_submission_permission, handle_errors, validate_json_data
from models.contest import Contest
from models.submission import Submission

# Create blueprint
submission_bp = Blueprint('submission', __name__)


def can_view_submissions(user, contest):
    """
    Check if user has permission to view submissions for a contest.

    Args:
        user: User object
        contest: Contest object

    Returns:
        bool: True if user has permission, False otherwise
    """
    return (user.is_admin() or
            user.is_contest_creator(contest) or
            user.is_jury_member(contest))

@submission_bp.route('/', methods=['GET'])
@require_auth
@handle_errors
def get_all_submissions():
    """
    Get all submissions (admin only)

    Returns:
        JSON response with all submissions
    """
    user = request.current_user

    if not user.is_admin():
        return jsonify({'error': 'Admin access required'}), 403

    submissions = Submission.query.order_by(Submission.submitted_at.desc()).all()

    submissions_data = []
    for submission in submissions:
        submission_data = submission.to_dict(include_user_info=True)
        submissions_data.append(submission_data)

    return jsonify(submissions_data), 200

@submission_bp.route('/<int:submission_id>', methods=['GET'])
@require_submission_permission('view')
@handle_errors
def get_submission_by_id(submission_id):  # pylint: disable=unused-argument
    """
    Get a specific submission by ID

    Args:
        submission_id: Submission ID

    Returns:
        JSON response with submission data
    """
    submission = request.current_submission

    # Get additional information
    submission_data = submission.to_dict(include_user_info=True)

    return jsonify(submission_data), 200

@submission_bp.route('/<int:submission_id>', methods=['PUT'])
@require_submission_permission('jury')
@handle_errors
@validate_json_data(['status'])
def update_submission_status(submission_id):  # pylint: disable=unused-argument
    """
    Update submission status and score (jury or admin only)

    Args:
        submission_id: Submission ID

    Expected JSON data:
        status: New status ('accepted' or 'rejected')

    Returns:
        JSON response with success message and updated status/score
    """
    submission = request.current_submission
    data = request.validated_data

    new_status = data['status'].strip().lower()

    # Validate status
    if new_status not in ['accepted', 'rejected']:
        return jsonify({'error': 'Status must be either "accepted" or "rejected"'}), 400

    # Check if status is already set
    if submission.status == new_status:
        return jsonify({
            'message': f'Submission is already {new_status}. No changes made.',
            'status': submission.status,
            'score': submission.score
        }), 200

    # Update submission status and score
    try:
        updated = submission.update_status(new_status)

        if updated:
            return jsonify({
                'message': 'Submission updated successfully',
                'status': submission.status,
                'score': submission.score
            }), 200
        return jsonify({
            'message': 'No changes made to submission',
            'status': submission.status,
            'score': submission.score
        }), 200

    except Exception:  # pylint: disable=broad-exception-caught
        # Log error for debugging but don't expose details to client
        return jsonify({'error': 'Failed to update submission'}), 500

@submission_bp.route('/user/<int:user_id>', methods=['GET'])
@require_auth
@handle_errors
def get_user_submissions(user_id):
    """
    Get all submissions by a specific user

    Args:
        user_id: User ID

    Returns:
        JSON response with user's submissions
    """
    current_user = request.current_user

    # Users can only view their own submissions unless they're admin
    if not current_user.is_admin() and current_user.id != user_id:
        return jsonify({'error': 'You can only view your own submissions'}), 403

    submissions = Submission.query.filter_by(user_id=user_id).order_by(
        Submission.submitted_at.desc()
    ).all()

    submissions_data = []
    for submission in submissions:
        submission_data = submission.to_dict(include_user_info=True)
        submissions_data.append(submission_data)

    return jsonify(submissions_data), 200

@submission_bp.route('/contest/<int:contest_id>', methods=['GET'])
@require_auth
@handle_errors
def get_contest_submissions(contest_id):  # pylint: disable=duplicate-code
    """
    Get all submissions for a specific contest

    Args:
        contest_id: Contest ID

    Returns:
        JSON response with contest submissions
    """
    user = request.current_user

    # Get contest
    contest = Contest.query.get(contest_id)
    if not contest:
        return jsonify({'error': 'Contest not found'}), 404

    # Check permissions
    if not can_view_submissions(user, contest):
        return jsonify({
            'error': 'You are not allowed to view submissions for this contest'
        }), 403

    submissions = Submission.query.filter_by(contest_id=contest_id).order_by(
        Submission.submitted_at.desc()
    ).all()

    submissions_data = []
    for submission in submissions:
        submission_data = submission.to_dict(include_user_info=True)
        submissions_data.append(submission_data)

    return jsonify(submissions_data), 200

@submission_bp.route('/pending', methods=['GET'])
@require_auth
@handle_errors
def get_pending_submissions():
    """
    Get all pending submissions that the user can judge

    Returns:
        JSON response with pending submissions
    """
    user = request.current_user

    # Get all pending submissions
    pending_submissions = Submission.query.filter_by(status='pending').all()

    # Filter submissions that user can judge
    judgeable_submissions = []
    for submission in pending_submissions:
        if submission.can_be_judged_by(user):
            submission_data = submission.to_dict(include_user_info=True)
            judgeable_submissions.append(submission_data)

    return jsonify(judgeable_submissions), 200

@submission_bp.route('/stats', methods=['GET'])
@require_auth
@handle_errors
def get_submission_stats():
    """
    Get submission statistics for the current user

    Returns:
        JSON response with submission statistics
    """
    user = request.current_user

    # Get user's submission statistics
    total_submissions = Submission.query.filter_by(user_id=user.id).count()
    accepted_submissions = Submission.query.filter_by(
        user_id=user.id,
        status='accepted'
    ).count()
    rejected_submissions = Submission.query.filter_by(
        user_id=user.id,
        status='rejected'
    ).count()
    pending_submissions = Submission.query.filter_by(
        user_id=user.id,
        status='pending'
    ).count()

    # Get total score from submissions
    total_score = db.session.query(db.func.sum(Submission.score)).filter_by(
        user_id=user.id
    ).scalar() or 0

    return jsonify({
        'total_submissions': total_submissions,
        'accepted_submissions': accepted_submissions,
        'rejected_submissions': rejected_submissions,
        'pending_submissions': pending_submissions,
        'total_score': total_score,
        'acceptance_rate': (accepted_submissions / total_submissions * 100) if total_submissions > 0 else 0
    }), 200
