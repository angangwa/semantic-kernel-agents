// Utility function to escape special regex characters
function escapeRegExp(string) {
    return string.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
}

class ContosoChat {
    constructor() {
        this.ws = null;
        this.sessionId = this.generateSessionId();
        this.isConnected = false;
        this.messageQueue = [];
        this.currentAgent = 'Alex';
        this.activeToolIndicators = new Map(); // Track active tool indicators
        this.hasStartedConversation = false; // Track if user has sent first message
        
        this.initializeElements();
        this.attachEventListeners();
        this.connect();
    }
    
    generateSessionId() {
        return 'session_' + Math.random().toString(36).substr(2, 9) + '_' + Date.now();
    }
    
    initializeElements() {
        this.elements = {
            messages: document.getElementById('messages'),
            messageInput: document.getElementById('message-input'),
            sendButton: document.getElementById('send-button'),
            agentName: document.getElementById('agent-name'),
            agentStatus: document.getElementById('agent-status'),
            connectionStatus: document.getElementById('connection-status'),
            connectionText: document.getElementById('connection-text'),
            statusDot: document.getElementById('status-dot'),
            loadingIndicator: document.getElementById('loading-indicator'),
            loadingAvatar: document.getElementById('loading-avatar'),
            loadingText: document.getElementById('loading-text'),
            conversationStarters: document.getElementById('conversation-starters'),
            resetButton: document.getElementById('reset-button'),
            architectureButton: document.getElementById('architecture-button'),
            fileModal: document.getElementById('file-modal'),
            modalTitle: document.getElementById('modal-title'),
            modalBody: document.getElementById('modal-body'),
            downloadButton: document.getElementById('download-button'),
            closeModal: document.getElementById('close-modal'),
            architectureModal: document.getElementById('architecture-modal'),
            architectureModalBody: document.getElementById('architecture-modal-body'),
            closeArchitectureModal: document.getElementById('close-architecture-modal'),
            architectureLoading: document.getElementById('architecture-loading')
        };
    }
    
    attachEventListeners() {
        // Send message on button click
        this.elements.sendButton.addEventListener('click', () => this.sendMessage());
        
        // Send message on Enter key
        this.elements.messageInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                this.sendMessage();
            }
        });
        
        // Conversation starters
        this.elements.conversationStarters.addEventListener('click', (e) => {
            if (e.target.classList.contains('starter-button')) {
                const message = e.target.getAttribute('data-message');
                this.sendMessage(message);
            }
        });
        
        // Reset button
        this.elements.resetButton.addEventListener('click', () => {
            this.resetChat();
        });
        
        // Architecture button
        this.elements.architectureButton.addEventListener('click', () => {
            this.openArchitectureModal();
        });
        
        // Modal close
        this.elements.closeModal.addEventListener('click', () => this.closeFileModal());
        this.elements.fileModal.addEventListener('click', (e) => {
            if (e.target === this.elements.fileModal) {
                this.closeFileModal();
            }
        });
        
        // Download button
        this.elements.downloadButton.addEventListener('click', () => this.downloadCurrentFile());
        
        // Architecture modal close
        this.elements.closeArchitectureModal.addEventListener('click', () => this.closeArchitectureModal());
        this.elements.architectureModal.addEventListener('click', (e) => {
            if (e.target === this.elements.architectureModal) {
                this.closeArchitectureModal();
            }
        });
    }
    
    connect() {
        try {
            const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
            const wsUrl = `${protocol}//${window.location.host}/ws/${this.sessionId}`;
            
            this.ws = new WebSocket(wsUrl);
            
            this.ws.onopen = () => {
                console.log('WebSocket connected');
                this.onConnected();
            };
            
            this.ws.onmessage = (event) => {
                const message = JSON.parse(event.data);
                this.handleMessage(message);
            };
            
            this.ws.onclose = () => {
                console.log('WebSocket disconnected');
                this.onDisconnected();
                // Attempt to reconnect after 3 seconds
                setTimeout(() => this.connect(), 3000);
            };
            
            this.ws.onerror = (error) => {
                console.error('WebSocket error:', error);
                this.onError();
            };
            
        } catch (error) {
            console.error('Failed to connect:', error);
            this.onError();
        }
    }
    
    onConnected() {
        this.isConnected = true;
        this.elements.connectionText.textContent = 'Connected';
        this.elements.statusDot.className = 'status-dot connected';
        this.elements.messageInput.disabled = false;
        this.elements.sendButton.disabled = false;
        
        // Process any queued messages
        while (this.messageQueue.length > 0) {
            const message = this.messageQueue.shift();
            this.sendMessage(message);
        }
    }
    
    onDisconnected() {
        this.isConnected = false;
        this.elements.connectionText.textContent = 'Disconnected';
        this.elements.statusDot.className = 'status-dot error';
        this.elements.messageInput.disabled = true;
        this.elements.sendButton.disabled = true;
        this.hideLoading();
    }
    
    onError() {
        this.elements.connectionText.textContent = 'Connection Error';
        this.elements.statusDot.className = 'status-dot error';
        this.elements.messageInput.disabled = true;
        this.elements.sendButton.disabled = true;
        this.hideLoading();
    }
    
    handleMessage(message) {
        console.log('Received message:', message);
        if (message.widgets) {
            console.log('DEBUG: Message has widgets:', message.widgets);
        }
        
        switch (message.type) {
            case 'system':
                this.addSystemMessage(message.content);
                break;
            case 'user_message':
                this.addUserMessage(message.content);
                break;
            case 'agent_message':
                this.addAgentMessage(message.agent, message.content, message.files, message.widgets);
                this.hideLoading();
                break;
            case 'tool_start':
                this.showToolIndicator(message.agent, message.tool);
                break;
            case 'tool_complete':
                this.hideToolIndicator(message.agent, message.tool);
                break;
            case 'agent_working':
                this.showAgentWorking(message.agent, message.content);
                break;
            case 'error':
                this.addErrorMessage(message.content);
                this.hideLoading();
                break;
            default:
                console.warn('Unknown message type:', message.type);
        }
    }
    
    sendMessage(text) {
        const message = text || this.elements.messageInput.value.trim();
        if (!message || !this.isConnected) {
            if (!this.isConnected && message) {
                this.messageQueue.push(message);
                this.addSystemMessage('Message queued. Waiting for connection...');
            }
            return;
        }
        
        // Clear input
        this.elements.messageInput.value = '';
        
        // Hide conversation starters after first message
        if (!this.hasStartedConversation) {
            this.hasStartedConversation = true;
            this.hideConversationStarters();
        }
        
        // Send to WebSocket
        this.ws.send(JSON.stringify({
            type: 'chat_message',
            content: message
        }));
        
        // Show loading
        this.showLoading();
    }
    
    addUserMessage(content) {
        const messageDiv = this.createMessageElement('user', 'You', content);
        this.elements.messages.appendChild(messageDiv);
        this.scrollToBottom();
    }
    
    addAgentMessage(agent, content, files = [], widgets = []) {
        console.log('DEBUG addAgentMessage called with:', { 
            agent, 
            content: content.substring(0, 200) + '...', 
            files, 
            widgets 
        });
        
        this.updateCurrentAgent(agent);
        
        // Clear any tool indicators for this agent when full message arrives
        this.clearAgentToolIndicators(agent);
        
        // Store widget HTML replacements with placeholders
        const widgetPlaceholders = new Map();
        let placeholderContent = content;
        
        // Replace widget patterns with placeholders before markdown parsing
        if (widgets && widgets.length > 0) {
            widgets.forEach((widget, index) => {
                const placeholder = `<!--WIDGET_PLACEHOLDER_${index}-->`;
                const widgetHtml = this.createWidgetPreview(widget);
                widgetPlaceholders.set(placeholder, widgetHtml);
                placeholderContent = placeholderContent.replace(widget.pattern, placeholder);
            });
        }
        
        // Process any remaining widget patterns in content (fallback)
        const widgetPattern = /\[WIDGET:([^:]+):(\[[^\]]*\])\]/g;
        let match;
        let fallbackIndex = widgets ? widgets.length : 0;
        
        while ((match = widgetPattern.exec(placeholderContent)) !== null) {
            const [fullMatch, widgetType, idsJson] = match;
            const placeholder = `<!--WIDGET_PLACEHOLDER_${fallbackIndex}-->`;
            const basicWidget = {
                widget_type: widgetType,
                widget_ids: [],
                widget_data: { widget_type: widgetType, title: `${widgetType} Widget`, data: [] },
                pattern: fullMatch
            };
            const widgetHtml = this.createWidgetPreview(basicWidget);
            widgetPlaceholders.set(placeholder, widgetHtml);
            placeholderContent = placeholderContent.replace(fullMatch, placeholder);
            fallbackIndex++;
        }
        
        // Render markdown (placeholders are safe from escaping)
        let processedContent = marked.parse(placeholderContent);
        
        // Replace placeholders with actual widget HTML
        widgetPlaceholders.forEach((widgetHtml, placeholder) => {
            processedContent = processedContent.replace(placeholder, widgetHtml);
        });
        
        // Process file references on the rendered HTML
        processedContent = this.processFileReferences(processedContent, files);
        
        const messageDiv = this.createMessageElement(agent.toLowerCase(), agent, processedContent);
        this.elements.messages.appendChild(messageDiv);
        this.scrollToBottom();
    }
    
    addSystemMessage(content) {
        const messageDiv = document.createElement('div');
        messageDiv.className = 'message system';
        messageDiv.innerHTML = `
            <div class="message-content">
                <div class="message-text" style="background: var(--contoso-bg-grey); border: 1px solid var(--contoso-border); font-style: italic;">
                    ${content}
                </div>
            </div>
        `;
        this.elements.messages.appendChild(messageDiv);
        this.scrollToBottom();
    }
    
    addErrorMessage(content) {
        const messageDiv = document.createElement('div');
        messageDiv.className = 'message error';
        messageDiv.innerHTML = `
            <div class="message-content">
                <div class="message-text text-error" style="background: #ffebee; border: 1px solid var(--contoso-blue);">
                    ❌ ${content}
                </div>
            </div>
        `;
        this.elements.messages.appendChild(messageDiv);
        this.scrollToBottom();
    }
    
    createMessageElement(agentClass, agentName, content) {
        const timestamp = new Date().toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'});
        
        const messageDiv = document.createElement('div');
        messageDiv.className = `message ${agentClass}`;
        
        messageDiv.innerHTML = `
            <div class="agent-avatar ${agentClass}"></div>
            <div class="message-content">
                <div class="message-header">
                    <span class="agent-name">${agentName}</span>
                    <span class="timestamp">${timestamp}</span>
                </div>
                <div class="message-text">
                    ${content}
                </div>
            </div>
        `;
        
        return messageDiv;
    }
    
    createFileArtifactHtml(file) {
        // Legacy method - now using inline artifact previews
        // This is kept for backwards compatibility but should not be used
        const icon = this.getFileIcon(file.file_type);
        return `
            <div class="file-artifact" data-file-id="${file.file_id}" data-file-type="${file.file_type}">
                <div class="file-artifact-header">
                    <span class="file-icon">${icon}</span>
                    <span class="file-name">${file.file_id}</span>
                </div>
                <div class="file-description">${file.description}</div>
            </div>
        `;
    }
    
    getFileIcon(fileType) {
        const icons = {
            'csv': '📊',
            'png': '🖼️',
            'jpg': '🖼️',
            'jpeg': '🖼️',
            'pdf': '📄',
            'json': '📋',
            'txt': '📝'
        };
        return icons[fileType.toLowerCase()] || '📁';
    }
    
    processFileReferences(content, files) {
        console.log('DEBUG processFileReferences:', { content: content.substring(0, 100), files });
        
        let processedContent = content;
        
        // First, process files from the files array if available
        if (files && files.length > 0) {
            console.log('Processing files from array:', files);
            files.forEach(file => {
                const pattern = new RegExp(`\\[FILE:${file.file_id}:[^\\]]+\\]`, 'g');
                const artifactHtml = this.createArtifactPreview(file);
                processedContent = processedContent.replace(pattern, artifactHtml);
            });
        }
        
        // Fallback: If files array is empty but [FILE:...] patterns exist, create basic artifacts
        const filePattern = /\[FILE:([^:]+):([^\]]+)\]/g;
        const remainingMatches = processedContent.match(filePattern);
        
        console.log('DEBUG remainingMatches:', remainingMatches);
        
        if (remainingMatches) {
            console.log('Processing fallback artifacts for:', remainingMatches);
            remainingMatches.forEach(match => {
                console.log('Processing match:', match);
                const [, fileId, description] = match.match(/\[FILE:([^:]+):([^\]]+)\]/);
                
                // Create basic file info from filename
                const fileExtension = fileId.split('.').pop().toLowerCase();
                const basicFile = {
                    file_id: fileId,
                    description: description,
                    file_type: fileExtension,
                    file_path: `/files/${fileId}`
                };
                
                console.log('Creating artifact for:', basicFile);
                const artifactHtml = this.createArtifactPreview(basicFile);
                console.log('Generated artifact HTML:', artifactHtml.substring(0, 100));
                processedContent = processedContent.replace(match, artifactHtml);
            });
        }
        
        console.log('Final processed content:', processedContent.substring(0, 200));
        return processedContent;
    }
    
    createArtifactPreview(file) {
        const fileType = file.file_type.toLowerCase();
        const icon = this.getFileIcon(fileType);
        
        if (fileType === 'png' || fileType === 'jpg' || fileType === 'jpeg') {
            // Inline image preview with click to expand
            return `
                <div class="artifact-preview image-artifact" data-file-id="${file.file_id}" data-file-type="${fileType}">
                    <div class="artifact-header">
                        <span class="artifact-icon">${icon}</span>
                        <span class="artifact-title">${file.description}</span>
                        <button class="download-btn" onclick="event.stopPropagation(); downloadFile('${file.file_id}')">⬇️</button>
                    </div>
                    <div class="artifact-content">
                        <img src="/files/${file.file_id}" alt="${file.description}" class="artifact-image" loading="lazy">
                        <div class="artifact-overlay">
                            <span>Click to view full size</span>
                        </div>
                    </div>
                </div>
            `;
        } else if (fileType === 'csv') {
            // CSV preview with click to open table view
            return `
                <div class="artifact-preview csv-artifact" data-file-id="${file.file_id}" data-file-type="${fileType}">
                    <div class="artifact-header">
                        <span class="artifact-icon">${icon}</span>
                        <span class="artifact-title">${file.description}</span>
                        <button class="download-btn" onclick="event.stopPropagation(); downloadFile('${file.file_id}')">⬇️</button>
                    </div>
                    <div class="artifact-content">
                        <div class="csv-preview-info">
                            <p>📊 Detailed data table</p>
                            <small>Click to view data or download CSV file</small>
                        </div>
                    </div>
                </div>
            `;
        } else {
            // Generic file artifact
            return `
                <div class="artifact-preview generic-artifact" data-file-id="${file.file_id}" data-file-type="${fileType}">
                    <div class="artifact-header">
                        <span class="artifact-icon">${icon}</span>
                        <span class="artifact-title">${file.description}</span>
                        <button class="download-btn" onclick="event.stopPropagation(); downloadFile('${file.file_id}')">⬇️</button>
                    </div>
                    <div class="artifact-content">
                        <div class="generic-preview-info">
                            <p>📄 ${fileType.toUpperCase()} File</p>
                            <small>Click to download</small>
                        </div>
                    </div>
                </div>
            `;
        }
    }
    
    processWidgetReferences(content, widgets) {
        console.log('DEBUG processWidgetReferences:', { 
            content: content.substring(0, 200) + '...', 
            widgetsLength: widgets ? widgets.length : 0,
            widgets: widgets 
        });
        
        let processedContent = content;
        
        // Process widgets from the widgets array if available
        if (widgets && widgets.length > 0) {
            console.log('Processing widgets from array:', widgets);
            widgets.forEach(widget => {
                const pattern = new RegExp(escapeRegExp(widget.pattern), 'g');
                const widgetHtml = this.createWidgetPreview(widget);
                processedContent = processedContent.replace(pattern, widgetHtml);
            });
        }
        
        // Fallback: If widgets array is empty but [WIDGET:...] patterns exist, create basic widgets
        const widgetPattern = /\[WIDGET:([^:]+):(\[[^\]]*\])\]/g;
        const remainingMatches = processedContent.match(widgetPattern);
        
        if (remainingMatches) {
            console.log('Processing fallback widgets for:', remainingMatches);
            remainingMatches.forEach(match => {
                console.log('Processing widget match:', match);
                const [, widgetType, idsJson] = match.match(/\[WIDGET:([^:]+):(\[[^\]]*\])/);
                
                // Create basic widget info from pattern
                const basicWidget = {
                    widget_type: widgetType,
                    widget_ids: [],
                    widget_data: { widget_type: widgetType, title: `${widgetType} Widget`, data: [] },
                    pattern: match
                };
                
                console.log('Creating fallback widget for:', basicWidget);
                const widgetHtml = this.createWidgetPreview(basicWidget);
                processedContent = processedContent.replace(match, widgetHtml);
            });
        }
        
        console.log('Final processed content with widgets:', processedContent.substring(0, 200));
        return processedContent;
    }
    
    createWidgetPreview(widget) {
        const widgetData = widget.widget_data;
        const widgetType = widgetData.widget_type;
        
        switch (widgetType) {
            case 'current_plan':
                return this.createCurrentPlanWidget(widgetData);
            case 'roaming_plans':
                return this.createRoamingPlansWidget(widgetData);
            case 'addons':
                return this.createAddonsWidget(widgetData);
            case 'usage_summary':
                return this.createUsageSummaryWidget(widgetData);
            case 'support_ticket':
                return this.createSupportTicketWidget(widgetData);
            default:
                return this.createGenericWidget(widgetData);
        }
    }
    
    createCurrentPlanWidget(data) {
        const plan = data.data;
        const includedFeatures = plan.included_features.map(f => `<li>✅ ${f}</li>`).join('');
        const actions = data.actions.map(action => 
            `<a href="${action.url}" target="_blank" class="widget-action ${action.type}">${action.label}</a>`
        ).join('');
        
        return `
            <div class="widget-preview current-plan-widget">
                <div class="widget-header">
                    <span class="widget-icon">📱</span>
                    <span class="widget-title">${data.title}</span>
                </div>
                <div class="widget-content">
                    <div class="plan-info">
                        <h3>${plan.plan_name}</h3>
                        <div class="plan-cost">£${plan.monthly_cost.toFixed(2)}/month</div>
                        <div class="plan-allowances">
                            <div class="allowance">📊 ${plan.data_allowance}</div>
                            <div class="allowance">📞 ${plan.minutes}</div>
                            <div class="allowance">💬 ${plan.texts}</div>
                        </div>
                        <div class="plan-features">
                            <h4>Included Features:</h4>
                            <ul>${includedFeatures}</ul>
                        </div>
                        <div class="contract-info">
                            <small>Contract ends: ${plan.contract_end_date}</small>
                        </div>
                    </div>
                    <div class="widget-actions">${actions}</div>
                </div>
            </div>
        `;
    }
    
    createRoamingPlansWidget(data) {
        const plans = data.data.map(plan => `
            <div class="roaming-plan-card">
                <div class="plan-header">
                    <h4>${plan.name}</h4>
                    <div class="plan-price">£${plan.price.toFixed(2)}</div>
                </div>
                <div class="plan-details">
                    <div class="detail">⏰ ${plan.duration}</div>
                    <div class="detail">📊 ${plan.data}</div>
                    <div class="detail">📞 ${plan.minutes}</div>
                    <div class="detail">💬 ${plan.texts}</div>
                </div>
                <div class="plan-countries">
                    <small>📍 ${plan.countries.join(', ')}</small>
                </div>
                <div class="savings-info">
                    <small>💰 ${plan.savings_example}</small>
                </div>
            </div>
        `).join('');
        
        const actions = data.actions.map(action => 
            `<a href="${action.url}" target="_blank" class="widget-action ${action.type}">${action.label}</a>`
        ).join('');
        
        return `
            <div class="widget-preview roaming-plans-widget">
                <div class="widget-header">
                    <span class="widget-icon">🌍</span>
                    <span class="widget-title">${data.title}</span>
                </div>
                <div class="widget-content">
                    <div class="roaming-plans-grid">${plans}</div>
                    <div class="widget-actions">${actions}</div>
                </div>
            </div>
        `;
    }
    
    createAddonsWidget(data) {
        const addons = data.data.map(addon => `
            <div class="addon-card">
                <div class="addon-header">
                    <h4>${addon.name}</h4>
                    <div class="addon-price">£${addon.price.toFixed(2)}</div>
                </div>
                <div class="addon-description">${addon.description}</div>
                <div class="addon-details">
                    <small>⏰ ${addon.duration}</small>
                    <small>⚡ ${addon.activation}</small>
                </div>
            </div>
        `).join('');
        
        const actions = data.actions.map(action => 
            `<a href="${action.url}" target="_blank" class="widget-action ${action.type}">${action.label}</a>`
        ).join('');
        
        return `
            <div class="widget-preview addons-widget">
                <div class="widget-header">
                    <span class="widget-icon">🔧</span>
                    <span class="widget-title">${data.title}</span>
                </div>
                <div class="widget-content">
                    <div class="addons-list">${addons}</div>
                    <div class="widget-actions">${actions}</div>
                </div>
            </div>
        `;
    }
    
    createUsageSummaryWidget(data) {
        const usage = data.data;
        const dataPercent = usage.data.percentage;
        const alerts = usage.alerts.map(alert => `<div class="usage-alert">⚠️ ${alert}</div>`).join('');
        
        const actions = data.actions.map(action => 
            `<a href="${action.url}" target="_blank" class="widget-action ${action.type}">${action.label}</a>`
        ).join('');
        
        return `
            <div class="widget-preview usage-summary-widget">
                <div class="widget-header">
                    <span class="widget-icon">📈</span>
                    <span class="widget-title">${data.title}</span>
                </div>
                <div class="widget-content">
                    <div class="usage-meters">
                        <div class="usage-meter">
                            <div class="meter-label">📊 Data Usage</div>
                            <div class="meter-bar">
                                <div class="meter-fill" style="width: ${dataPercent}%"></div>
                            </div>
                            <div class="meter-text">${usage.data.used} of ${usage.data.total} (${dataPercent}%)</div>
                        </div>
                        <div class="usage-stats">
                            <div class="stat">📞 ${usage.minutes.used} minutes</div>
                            <div class="stat">💬 ${usage.texts.used} texts</div>
                            <div class="stat">📅 ${usage.days_remaining} days remaining</div>
                        </div>
                    </div>
                    <div class="usage-alerts">${alerts}</div>
                    <div class="widget-actions">${actions}</div>
                </div>
            </div>
        `;
    }
    
    createSupportTicketWidget(data) {
        const ticket = data.data;
        const actions = data.actions.map(action => 
            `<a href="${action.url}" target="_blank" class="widget-action ${action.type}">${action.label}</a>`
        ).join('');
        
        // Status color based on ticket status
        const statusClass = ticket.status === 'Open' ? 'status-open' : 
                           ticket.status === 'In Progress' ? 'status-progress' : 'status-closed';
        
        return `
            <div class="widget-preview support-ticket-widget">
                <div class="widget-header">
                    <span class="widget-icon">🎫</span>
                    <span class="widget-title">${data.title}</span>
                </div>
                <div class="widget-content">
                    <div class="ticket-summary">
                        <div class="ticket-header">
                            <div class="ticket-id">
                                <strong>Ticket #${ticket.ticket_id}</strong>
                                <span class="ticket-status ${statusClass}">${ticket.status}</span>
                            </div>
                            <div class="ticket-priority">Priority: ${ticket.priority}</div>
                        </div>
                        
                        <div class="ticket-details">
                            <div class="ticket-row">
                                <span class="ticket-label">📅 Created:</span>
                                <span class="ticket-value">${ticket.created_date}</span>
                            </div>
                            <div class="ticket-row">
                                <span class="ticket-label">📋 Subject:</span>
                                <span class="ticket-value">${ticket.subject}</span>
                            </div>
                            <div class="ticket-row">
                                <span class="ticket-label">📞 Contact Method:</span>
                                <span class="ticket-value">${ticket.contact_method}</span>
                            </div>
                            <div class="ticket-row">
                                <span class="ticket-label">⏱️ Estimated Response:</span>
                                <span class="ticket-value">${ticket.estimated_callback}</span>
                            </div>
                            <div class="ticket-row">
                                <span class="ticket-label">👥 Assigned Team:</span>
                                <span class="ticket-value">${ticket.assigned_team}</span>
                            </div>
                        </div>
                        
                        <div class="ticket-description">
                            <strong>Description:</strong>
                            <p>${ticket.description}</p>
                        </div>
                        
                        <div class="ticket-reference">
                            <small><strong>Reference:</strong> ${ticket.reference_number}</small>
                        </div>
                    </div>
                    <div class="widget-actions">${actions}</div>
                </div>
            </div>
        `;
    }
    
    createGenericWidget(data) {
        return `
            <div class="widget-preview generic-widget">
                <div class="widget-header">
                    <span class="widget-icon">🔧</span>
                    <span class="widget-title">${data.title || 'Widget'}</span>
                </div>
                <div class="widget-content">
                    <p>Widget type: ${data.widget_type}</p>
                    <small>This widget type is not yet implemented.</small>
                </div>
            </div>
        `;
    }
    
    showLoading() {
        this.elements.loadingIndicator.style.display = 'flex';
        this.elements.loadingAvatar.className = `agent-avatar ${this.currentAgent.toLowerCase()}`;
        this.scrollToBottom();
    }
    
    hideLoading() {
        this.elements.loadingIndicator.style.display = 'none';
    }
    
    showToolIndicator(agent, tool) {
        this.updateCurrentAgent(agent);
        
        const toolEmoji = this.getToolEmoji(tool);
        const toolKey = `${agent}-${tool}`;
        
        // Remove existing indicator for this tool if it exists
        if (this.activeToolIndicators.has(toolKey)) {
            const existingIndicator = this.activeToolIndicators.get(toolKey);
            existingIndicator.remove();
        }
        
        // Create new tool indicator
        const indicatorDiv = document.createElement('div');
        indicatorDiv.className = 'tool-indicator';
        indicatorDiv.setAttribute('data-tool-key', toolKey);
        
        indicatorDiv.innerHTML = `
            <div class="agent-avatar ${agent.toLowerCase()}"></div>
            <div class="tool-indicator-content">
                <span class="tool-emoji">${toolEmoji}</span>
                <span class="tool-text">${this.getToolDisplayName(tool)}</span>
                <span class="tool-agent">${agent}</span>
            </div>
        `;
        
        this.elements.messages.appendChild(indicatorDiv);
        this.activeToolIndicators.set(toolKey, indicatorDiv);
        this.scrollToBottom();
    }
    
    hideToolIndicator(agent, tool) {
        const toolKey = `${agent}-${tool}`;
        if (this.activeToolIndicators.has(toolKey)) {
            const indicator = this.activeToolIndicators.get(toolKey);
            // Wait 2 seconds before starting fade out
            setTimeout(() => {
                indicator.classList.add('fade-out');
                setTimeout(() => {
                    if (indicator.parentNode) {
                        indicator.remove();
                    }
                    this.activeToolIndicators.delete(toolKey);
                }, 500); // Fade out animation duration
            }, 2000); // Wait 2 seconds before fading
        }
    }
    
    clearAgentToolIndicators(agent) {
        // Remove all tool indicators for this agent when their full message arrives
        for (const [toolKey, indicator] of this.activeToolIndicators.entries()) {
            if (toolKey.startsWith(agent + '-')) {
                // Wait 1.5 seconds before starting fade out when message arrives
                setTimeout(() => {
                    indicator.classList.add('fade-out');
                    setTimeout(() => {
                        if (indicator.parentNode) {
                            indicator.remove();
                        }
                        this.activeToolIndicators.delete(toolKey);
                    }, 500); // Fade out animation duration
                }, 1500); // Wait 1.5 seconds before fading when message arrives
            }
        }
    }
    
    getToolEmoji(tool) {
        const toolEmojis = {
            'get_recent_bills': '📊',
            'get_bill_details': '📋',
            'analyze_high_charges': '🔍',
            'calculate_bill_item': '🧮',
            'get_current_plan': '📱',
            'get_available_addons': '➕',
            'get_roaming_plans': '🌍',
            'get_usage_summary': '📈',
            'create_support_ticket': '🎫',
            'schedule_callback': '📞',
            'get_self_service_options': '🛠️',
            'Handoff': '🔄'
        };
        
        // Handle tool names that contain prefixes
        for (const [toolName, emoji] of Object.entries(toolEmojis)) {
            if (tool.includes(toolName)) {
                return emoji;
            }
        }
        
        return '⚙️'; // Default tool emoji
    }
    
    getToolDisplayName(tool) {
        const toolNames = {
            'get_recent_bills': 'Getting recent bills',
            'get_bill_details': 'Fetching bill details',
            'analyze_high_charges': 'Analyzing charges',
            'calculate_bill_item': 'Calculating costs',
            'get_current_plan': 'Checking current plan',
            'get_available_addons': 'Finding addons',
            'get_roaming_plans': 'Checking roaming plans',
            'get_usage_summary': 'Getting usage data',
            'create_support_ticket': 'Creating support ticket',
            'schedule_callback': 'Scheduling callback',
            'get_self_service_options': 'Finding self-service options',
            'transfer_to_BillingAgent': 'Connecting to billing specialist',
            'transfer_to_PlanAgent': 'Connecting to plan advisor',
            'transfer_to_SupportAgent': 'Connecting to support agent'
        };
        
        // Handle tool names that contain prefixes or suffixes
        for (const [toolName, displayName] of Object.entries(toolNames)) {
            if (tool.includes(toolName)) {
                return displayName;
            }
        }
        
        // Fallback: clean up the tool name
        return tool.replace(/[_-]/g, ' ').replace(/([A-Z])/g, ' $1').toLowerCase().trim();
    }
    
    showAgentWorking(agent, content) {
        this.updateCurrentAgent(agent);
        this.elements.loadingText.textContent = content;
        this.showLoading();
    }
    
    updateCurrentAgent(agent) {
        this.currentAgent = agent;
        this.elements.agentName.textContent = agent;
        this.elements.agentStatus.textContent = 'Active';
        
        // Update loading avatar if visible
        if (this.elements.loadingIndicator.style.display === 'flex') {
            this.elements.loadingAvatar.className = `agent-avatar ${agent.toLowerCase()}`;
        }
    }
    
    hideConversationStarters() {
        this.elements.conversationStarters.style.display = 'none';
    }
    
    showConversationStarters() {
        this.elements.conversationStarters.style.display = 'block';
    }
    
    resetChat() {
        // Store the welcome message
        const welcomeMessage = this.elements.messages.querySelector('.welcome-message');
        const welcomeMessageHTML = welcomeMessage ? welcomeMessage.outerHTML : '';
        
        // Clear all messages
        this.elements.messages.innerHTML = welcomeMessageHTML;
        
        // Reset conversation state
        this.hasStartedConversation = false;
        
        // Show conversation starters again
        this.showConversationStarters();
        
        // Reset current agent
        this.currentAgent = 'Alex';
        this.updateCurrentAgent('Alex');
        
        // Clear any active tool indicators
        this.activeToolIndicators.clear();
        
        // Hide loading
        this.hideLoading();
        
        // Clear input
        this.elements.messageInput.value = '';
        
        // Generate new session ID for fresh start
        this.sessionId = this.generateSessionId();
        
        // Reconnect with new session
        if (this.ws) {
            this.ws.close();
        }
        setTimeout(() => {
            this.connect();
        }, 100);
    }
    
    scrollToBottom() {
        setTimeout(() => {
            this.elements.messages.scrollTop = this.elements.messages.scrollHeight;
        }, 100);
    }
    
    // File modal functionality
    async openFileModal(fileId, fileType) {
        try {
            this.elements.modalTitle.textContent = `File: ${fileId}`;
            this.elements.downloadButton.setAttribute('data-file-id', fileId);
            
            if (fileType === 'csv') {
                await this.loadCsvPreview(fileId);
            } else if (['png', 'jpg', 'jpeg'].includes(fileType)) {
                await this.loadImagePreview(fileId);
            } else {
                this.elements.modalBody.innerHTML = `
                    <p>File preview not available for ${fileType} files.</p>
                    <p>Click download to save the file.</p>
                `;
            }
            
            this.elements.fileModal.style.display = 'flex';
        } catch (error) {
            console.error('Error opening file modal:', error);
            this.addErrorMessage('Failed to load file preview');
        }
    }
    
    async loadCsvPreview(fileId) {
        try {
            const response = await fetch(`/files/${fileId}`);
            const csvText = await response.text();
            
            const lines = csvText.trim().split('\n');
            const headers = lines[0].split(',');
            const rows = lines.slice(1).map(line => line.split(','));
            
            let tableHtml = '<table class="csv-table"><thead><tr>';
            headers.forEach(header => {
                tableHtml += `<th>${header.trim()}</th>`;
            });
            tableHtml += '</tr></thead><tbody>';
            
            rows.slice(0, 50).forEach(row => { // Limit to first 50 rows
                tableHtml += '<tr>';
                row.forEach(cell => {
                    tableHtml += `<td>${cell.trim()}</td>`;
                });
                tableHtml += '</tr>';
            });
            
            tableHtml += '</tbody></table>';
            
            if (rows.length > 50) {
                tableHtml += `<p><em>Showing first 50 of ${rows.length} rows. Download to see all data.</em></p>`;
            }
            
            this.elements.modalBody.innerHTML = tableHtml;
        } catch (error) {
            console.error('Error loading CSV preview:', error);
            this.elements.modalBody.innerHTML = '<p>Error loading CSV preview</p>';
        }
    }
    
    async loadImagePreview(fileId) {
        try {
            const imageUrl = `/files/${fileId}`;
            this.elements.modalBody.innerHTML = `
                <div class="image-preview">
                    <img src="${imageUrl}" alt="File preview" />
                </div>
            `;
        } catch (error) {
            console.error('Error loading image preview:', error);
            this.elements.modalBody.innerHTML = '<p>Error loading image preview</p>';
        }
    }
    
    closeFileModal() {
        this.elements.fileModal.style.display = 'none';
        this.elements.modalBody.innerHTML = '';
    }
    
    // Architecture modal functionality
    async openArchitectureModal() {
        try {
            // Show modal with loading state
            this.elements.architectureModal.style.display = 'flex';
            this.elements.architectureLoading.style.display = 'block';
            this.elements.architectureModalBody.innerHTML = '<div class="loading-spinner" id="architecture-loading">Loading documentation...</div>';
            
            // Fetch architecture documentation
            const response = await fetch('/demo-architecture');
            if (!response.ok) {
                throw new Error(`Failed to load documentation: ${response.status}`);
            }
            
            const data = await response.json();
            
            // Parse markdown and render
            this.renderArchitectureContent(data.content);
            
        } catch (error) {
            console.error('Error loading architecture documentation:', error);
            this.elements.architectureModalBody.innerHTML = `
                <div class="error-message">
                    <p>Failed to load architecture documentation.</p>
                    <p>Error: ${error.message}</p>
                </div>
            `;
        }
    }
    
    renderArchitectureContent(markdownContent) {
        // Initialize Mermaid
        if (typeof mermaid !== 'undefined') {
            mermaid.initialize({
                startOnLoad: false,
                theme: 'default',
                securityLevel: 'loose',
                fontFamily: 'Arial, sans-serif'
            });
        }
        
        // Process Mermaid diagrams first
        let content = markdownContent;
        const mermaidDiagrams = [];
        let mermaidCounter = 0;
        
        content = content.replace(/```mermaid\n([\s\S]*?)```/gim, (match, diagram) => {
            const id = `mermaid-${mermaidCounter++}`;
            mermaidDiagrams.push({ id, diagram: diagram.trim() });
            return `<div class="mermaid-placeholder" data-id="${id}"></div>`;
        });
        
        // Use marked.js for proper markdown parsing
        if (typeof marked !== 'undefined') {
            const html = marked.parse(content);
            this.elements.architectureModalBody.innerHTML = html;
        } else {
            // Fallback if marked.js isn't loaded
            this.elements.architectureModalBody.innerHTML = content.replace(/\n/g, '<br>');
        }
        
        // Render Mermaid diagrams
        this.renderMermaidDiagrams(mermaidDiagrams);
    }
    
    async renderMermaidDiagrams(diagrams) {
        if (typeof mermaid === 'undefined' || diagrams.length === 0) return;
        
        for (const { id, diagram } of diagrams) {
            try {
                const placeholder = this.elements.architectureModalBody.querySelector(`[data-id="${id}"]`);
                if (placeholder) {
                    // Create a container for the mermaid diagram
                    const container = document.createElement('div');
                    container.className = 'mermaid-diagram';
                    container.innerHTML = diagram;
                    
                    // Replace placeholder with container
                    placeholder.parentNode.replaceChild(container, placeholder);
                    
                    // Render the mermaid diagram
                    await mermaid.init(undefined, container);
                }
            } catch (error) {
                console.error('Error rendering Mermaid diagram:', error);
                const placeholder = this.elements.architectureModalBody.querySelector(`[data-id="${id}"]`);
                if (placeholder) {
                    placeholder.innerHTML = `<pre>Error rendering diagram:\n${diagram}</pre>`;
                    placeholder.className = 'mermaid-error';
                }
            }
        }
    }
    
    closeArchitectureModal() {
        this.elements.architectureModal.style.display = 'none';
        this.elements.architectureModalBody.innerHTML = '';
    }
    
    downloadCurrentFile() {
        const fileId = this.elements.downloadButton.getAttribute('data-file-id');
        if (fileId) {
            const link = document.createElement('a');
            link.href = `/files/${fileId}`;
            link.download = fileId;
            document.body.appendChild(link);
            link.click();
            document.body.removeChild(link);
        }
    }
}

// Global download function for artifact buttons
function downloadFile(fileId) {
    const link = document.createElement('a');
    link.href = `/files/${fileId}`;
    link.download = fileId;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
}

// Initialize the chat when the page loads
document.addEventListener('DOMContentLoaded', () => {
    const chat = new ContosoChat();
    
    // Handle artifact clicks (new system)
    document.addEventListener('click', (e) => {
        // Handle artifact preview clicks
        if (e.target.classList.contains('artifact-preview') || e.target.closest('.artifact-preview')) {
            const artifact = e.target.closest('.artifact-preview') || e.target;
            const fileId = artifact.getAttribute('data-file-id');
            const fileType = artifact.getAttribute('data-file-type');
            
            // Don't open modal if download button was clicked
            if (e.target.classList.contains('download-btn')) {
                return;
            }
            
            chat.openFileModal(fileId, fileType);
        }
        
        // Handle legacy file artifact clicks (backwards compatibility)
        if (e.target.classList.contains('file-artifact') || e.target.closest('.file-artifact')) {
            const artifact = e.target.closest('.file-artifact') || e.target;
            const fileId = artifact.getAttribute('data-file-id');
            const fileType = artifact.getAttribute('data-file-type');
            chat.openFileModal(fileId, fileType);
        }
        
        // Handle inline file references
        if (e.target.classList.contains('file-reference')) {
            const fileId = e.target.getAttribute('data-file-id');
            chat.openFileModal(fileId, 'csv'); // Default to CSV for now
        }
    });
});