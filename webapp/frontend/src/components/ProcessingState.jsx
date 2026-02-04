import React from 'react';

/**
 * ProcessingState Component
 * Shows clear visual indication of current processing state
 * For research demonstration
 */

export const ProcessingState = ({ phase, status, progress = 0, message = '' }) => {
    const getStatusIcon = () => {
        switch (status) {
            case 'complete':
                return (
                    <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
                        <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
                    </svg>
                );
            case 'running':
                return <div className="processing-spinner" />;
            case 'error':
                return (
                    <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
                        <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clipRule="evenodd" />
                    </svg>
                );
            default:
                return (
                    <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
                        <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm1-12a1 1 0 10-2 0v4a1 1 0 00.293.707l2.828 2.829a1 1 0 101.415-1.415L11 9.586V6z" clipRule="evenodd" />
                    </svg>
                );
        }
    };

    const getPhaseTitle = () => {
        const titles = {
            1: 'Text Extraction & Simplification',
            2: 'LLM Classification',
            3: 'FOL Formalization',
            4: 'SHACL Translation'
        };
        return titles[phase] || 'Processing';
    };

    return (
        <div className={`phase-card phase-${status}`}>
            <div className="flex items-center gap-3 mb-3">
                <div className={`phase-number ${status === 'complete' ? 'complete' : ''}`}>
                    {phase}
                </div>
                <div className="flex-1">
                    <h3 className="font-semibold text-lg text-gray-800">{getPhaseTitle()}</h3>
                    <div className={`status-badge ${status} mt-1`}>
                        {getStatusIcon()}
                        <span className="capitalize">{status}</span>
                    </div>
                </div>
            </div>

            {status === 'running' && (
                <>
                    <div className="progress-bar-container mt-3">
                        <div
                            className="progress-bar-fill animated"
                            style={{ width: `${progress}%` }}
                        />
                    </div>
                    {message && (
                        <p className="text-sm text-gray-600 mt-2">{message}</p>
                    )}
                </>
            )}

            {status === 'complete' && message && (
                <div className="alert alert-success mt-3">
                    <strong>✓</strong> {message}
                </div>
            )}

            {status === 'error' && message && (
                <div className="alert alert-error mt-3">
                    <strong>✗</strong> {message}
                </div>
            )}
        </div>
    );
};

/**
 * PipelineProgress Component
 * Shows overall pipeline progress with 4 phases
 */
export const PipelineProgress = ({ phases }) => {
    const completedCount = phases.filter(p => p.status === 'complete').length;
    const overallProgress = (completedCount / phases.length) * 100;

    return (
        <div className="card mb-6">
            <div className="card-header">
                <span className="text-gradient">4-Phase Pipeline Progress</span>
            </div>

            <div className="mb-4">
                <div className="flex justify-between items-center mb-2">
                    <span className="text-sm font-medium text-gray-700">
                        Overall Progress
                    </span>
                    <span className="text-sm font-bold text-primary-600">
                        {Math.round(overallProgress)}%
                    </span>
                </div>
                <div className="progress-bar-container h-3">
                    <div
                        className={`progress-bar-fill ${overallProgress < 100 ? 'animated' : ''}`}
                        style={{ width: `${overallProgress}%` }}
                    />
                </div>
            </div>

            <div className="grid gap-4">
                {phases.map((phase, index) => (
                    <ProcessingState key={index} {...phase} />
                ))}
            </div>
        </div>
    );
};

/**
 * StatsGrid Component
 * Display research statistics in bright cards
 */
export const StatsGrid = ({ stats }) => {
    return (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
            {stats.map((stat, index) => (
                <div key={index} className="stat-card fade-in" style={{ animationDelay: `${index * 0.1}s` }}>
                    <div className="stat-value">{stat.value}</div>
                    <div className="stat-label">{stat.label}</div>
                    {stat.sublabel && (
                        <div className="text-xs text-gray-500 mt-1">{stat.sublabel}</div>
                    )}
                </div>
            ))}
        </div>
    );
};

/**
 * StatusIndicator Component
 * Simple inline status indicator
 */
export const StatusIndicator = ({ status, text }) => {
    return (
        <span className={`status-badge ${status}`}>
            {status === 'running' && <div className="processing-spinner" />}
            {status === 'complete' && '✓'}
            {status === 'error' && '✗'}
            {status === 'pending' && '⏳'}
            <span>{text || status}</span>
        </span>
    );
};

export default {
    ProcessingState,
    PipelineProgress,
    StatsGrid,
    StatusIndicator
};
