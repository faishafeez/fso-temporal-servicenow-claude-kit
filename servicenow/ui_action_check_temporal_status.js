// UI Action: "Check Temporal Status"
// Action name: check_temporal_status
// Table: whatever your complaint/case table is (demo used u_insurance_complaint_case)
// Form button: checked | Show insert: unchecked | Show update: checked
//
// Behavior: if no Temporal workflow exists yet for this record, starts one.
// If one already exists, pulls its current status onto the record and
// creates a task if a NIGO is blocking things.
//
// Requires the system property x_temporal.gateway_url to be set to your
// gateway's reachable URL (see ../README.md).
//
// Field names below (u_fraud_check_complete, etc.) match the demo's table.
// Adjust to your own field names before use.

(function() {
    var gatewayUrl = gs.getProperty('x_temporal.gateway_url');
    var complaintId = current.number.toString(); // works for any record number format

    var statusRequest = new sn_ws.RESTMessageV2();
    statusRequest.setEndpoint(gatewayUrl + '/complaints/' + complaintId + '/status');
    statusRequest.setHttpMethod('GET');
    var statusResponse = statusRequest.execute();
    var result = JSON.parse(statusResponse.getBody());

    if (!result.found) {
        // No Temporal workflow exists yet for this complaint — start one now.
        // Falls back to the complaint number itself if there's no policy number field.
        var policyNumber = current.u_policy_number ? current.u_policy_number.toString() : complaintId;

        var startRequest = new sn_ws.RESTMessageV2();
        startRequest.setEndpoint(gatewayUrl + '/complaints/' + complaintId + '/start-research');
        startRequest.setHttpMethod('POST');
        startRequest.setRequestHeader('Content-Type', 'application/json');
        startRequest.setRequestBody(JSON.stringify({
            complaint_id: complaintId,
            policy_number: policyNumber
        }));
        var startResponse = startRequest.execute();

        if (startResponse.getStatusCode() == 200) {
            gs.addInfoMessage('Temporal research started for ' + complaintId +
                '. Click "Check Temporal Status" again in a few seconds to see progress.');
        } else {
            gs.addErrorMessage('Could not start Temporal research: ' + startResponse.getBody());
        }
        return;
    }

    // A workflow already exists for this complaint — pull its current state.
    current.u_fraud_check_complete = result.fraud_check_done;
    current.u_claim_history_reviewed = result.complaint_history_done;
    current.u_document_review_complete = result.document_review_complete;

    if (result.fraud_check_done && result.fraud_risk_score) {
        var riskMap = { 'low': 'Low', 'medium': 'Medium', 'high': 'High' };
        current.u_fraud_risk_score = riskMap[result.fraud_risk_score] || result.fraud_risk_score;
    }

    if (result.document_status) {
        current.u_document_status = result.document_status; // "NIGO-Missing Documents" or "IGO"
    }

    if (result.nigo_flagged && !result.nigo_resolved) {
        var task = new GlideRecord('task');
        task.initialize();
        task.short_description = 'Missing document for ' + complaintId + ': ' + result.nigo_reason;
        task.description = 'Temporal flagged a NIGO while researching complaint ' +
            complaintId + '. Please obtain the missing document from the customer ' +
            'and record the endorsement date to resolve.';
        task.insert();
        gs.addInfoMessage('NIGO detected — task created for missing document (' + complaintId + ').');
    } else if (result.nigo_flagged && result.nigo_resolved) {
        gs.addInfoMessage('NIGO already resolved — Research should complete shortly.');
    } else {
        gs.addInfoMessage('Fraud check and claim history check complete. No NIGO yet.');
    }

    current.update();
    action.setRedirectURL(current);
})();
