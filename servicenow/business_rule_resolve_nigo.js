// Business Rule: "Resolve Temporal NIGO on Document Review Complete"
// Table: whatever your complaint/case table is (demo used u_insurance_complaint_case)
// When: after | Insert: unchecked | Update: checked
// Condition (use the visual condition builder, no scripting needed):
//     Document Status  changes to  IGO
//
// Behavior: the moment someone marks the missing document resolved (by
// flipping the Document Status field to IGO), this signals the paused
// Temporal workflow to resume.
//
// Requires the system property x_temporal.gateway_url to be set.

(function executeRule(current, previous /*null when async*/) {

    var gatewayUrl = gs.getProperty('x_temporal.gateway_url');
    var complaintId = current.number.toString();
    var endorsementDate = new GlideDateTime().getDate().toString(); // today's date

    var request = new sn_ws.RESTMessageV2();
    request.setEndpoint(gatewayUrl + '/complaints/' + complaintId + '/resolve-nigo');
    request.setHttpMethod('POST');
    request.setRequestHeader('Content-Type', 'application/json');
    request.setRequestBody(JSON.stringify({ endorsement_date: endorsementDate }));

    var response = request.execute();

    if (response.getStatusCode() == 200) {
        gs.addInfoMessage('Sent resolution to Temporal for ' + complaintId + ' \u2014 Research should complete shortly.');
    } else {
        gs.addErrorMessage('Could not signal Temporal: ' + response.getBody());
    }

})(current, previous);
