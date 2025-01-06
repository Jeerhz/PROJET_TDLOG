//////////// HOW TO USE ////////////
/*
<display-edit-form
        save-url="{% url 'save_changes'%}"
        title="Infos étudiant"
        data-items='[
        {"label": "Name", "name": "student-name", "type": "char", "value": "John Doe", "duress": "readonly"},
        {"label": "Email", "name": "student-email", "type": "char", "value": "john@example.com", "duress": "required"},
        {"label": "Phone", "name": "student-phone", "type": "int", "value": "+1234567890"}
        ]'>
        {% csrf_token %}
</display-edit-form>
*/
////////////////////////////////////


class DisplayEditForm extends HTMLElement {
    constructor() {
        super();
        this.isEditMode = false;
        // Bind the methods to preserve 'this' context
        this.toggleEditMode = this.toggleEditMode.bind(this);
        this.saveChanges = this.saveChanges.bind(this);
        this.cancelEdit = this.cancelEdit.bind(this);
    }

    static get observedAttributes() {
        return ['data-items'];
    }

    connectedCallback() {
        this.render();
        this.attachEventListeners();
    }

    get items() {
        try {
            return JSON.parse(this.getAttribute('data-items'));
        } catch {
            return [];
        }
    }

    attachEventListeners() {
        // Remove any existing event listeners first
        this.removeEventListeners();
        
        // Store references to buttons
        this.editButton = this.querySelector('.edit-button');
        this.saveButton = this.querySelector('.save-button');
        this.cancelButton = this.querySelector('.cancel-button');

        // Add new event listeners
        if (this.editButton) {
            this.editButton.addEventListener('click', this.toggleEditMode);
        }
        if (this.saveButton) {
            this.saveButton.addEventListener('click', this.saveChanges);
        }
        if (this.cancelButton) {
            this.cancelButton.addEventListener('click', this.cancelEdit);
        }
    }

    removeEventListeners() {
        // Remove existing event listeners if buttons exist
        if (this.editButton) {
            this.editButton.removeEventListener('click', this.toggleEditMode);
        }
        if (this.saveButton) {
            this.saveButton.removeEventListener('click', this.saveChanges);
        }
        if (this.cancelButton) {
            this.cancelButton.removeEventListener('click', this.cancelEdit);
        }
    }

    disconnectedCallback() {
        // Clean up event listeners when component is removed
        this.removeEventListeners();
    }

    toggleEditMode() {
        this.isEditMode = !this.isEditMode;
        this.render();
    }

    async saveChanges() {
        const form = this.querySelector('form');
        const formData = new FormData(form);
        try {
            const response = await fetch(this.getAttribute('save-url'), {
                method: 'POST',
                headers: {
                    'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value
                },
                body: formData
            });

            if (!response.ok) throw new Error('Save failed');

            const data = await response.json();
            this.setAttribute('data-items', JSON.stringify(data));
            this.isEditMode = false;
            this.render();
        } catch (error) {
            console.error('Save failed:', error);
            alert('Failed to save changes');
        }
    }

    cancelEdit() {
        this.isEditMode = false;
        this.render();
    }

    render() {
        const items = this.items;
        
        this.innerHTML = `
            <div class="card shadow">
                ${this.hasAttribute("title") ? 
                `<div class="card-header">
                    <strong>${this.getAttribute("title")}</strong>
                </div>` : ''}
                <div class="card-body">
                    ${this.isEditMode ? this.renderEditMode(items) : this.renderDisplayMode(items)}
                </div>
            </div>
        `;

        this.attachEventListeners();
    }

    renderDisplayMode(items) {
        return `
            <div class="list-group list-group-flush">
                ${items.map(item => `
                    <li class="list-group-item d-flex justify-content-between">
                        <strong>${item.label}</strong>
                        <span>${item.value}</span>
                    </li>
                `).join('')}
            </div>
            <div class="text-end mt-3">
                <button type="button" class="btn btn-outline-secondary mt-3 edit-button">
                    <i class="bi bi-pencil"></i> Modify
                </button>
            </div>
        `;
    }

    renderEditMode(items) {
        return `
            <form>
                <div class="list-group list-group-flush">
                    ${items.map((item, index) => `
                        <li class="list-group-item d-flex">
                            <div class="col-4">
                            <strong>${item.label}</strong>
                            </div>
                            <div class="col-8">
                            <input type="${item.type}" 
                                class="form-control" 
                                name="${item.name}" 
                                value="${item.value}" 
                                ${item.duress}>
                            </div>
                        </li>
                    `).join('')}
                </div>
                <div class="row justify-content-between mt-3">
                    <div class="col-auto">
                        <button type="button" class="btn btn-outline-secondary mt-3 cancel-button">Cancel</button>
                    </div>
                    <div class="col-auto">
                        <button type="button" class="btn btn-outline-success mt-3 save-button">Save</button>
                    </div>
                </div>
            </form>
        `;
    }
}

customElements.define('display-edit-form', DisplayEditForm);