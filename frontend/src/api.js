
const API_BASE_URL = "http://localhost:8000";

export async function getCases() {
  const response = await fetch(`${API_BASE_URL}/cases`);

  if (!response.ok) {
    throw new Error("Failed to fetch cases from the server");
  }

  const data = await response.json();
  return data.cases;
}

export async function getCrimes() {
  const response = await fetch(`${API_BASE_URL}/crimes`);

  if (!response.ok) {
    throw new Error("Failed to fetch crime records");
  }

  const data = await response.json();
  return data.crimes;
}

export async function getOfficers() {
  const response = await fetch(`${API_BASE_URL}/officers`);

  if (!response.ok) {
    throw new Error("Failed to fetch officer records");
  }

  const data = await response.json();
  return data.officers;
}

export async function createCase(caseData) {
  const response = await fetch(`${API_BASE_URL}/cases`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(caseData),
  });

  const data = await response.json();

  if (!response.ok) {
    throw new Error(data.detail || "Failed to create case record");
  }

  return data;
}

export async function updateCase(caseId, updates) {
  const response = await fetch(`${API_BASE_URL}/cases/${caseId}`, {
    method: "PUT",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(updates),
  });

  const data = await response.json();

  if (!response.ok) {
    throw new Error(data.detail || "Failed to update case");
  }

  return data;
}

// Fetch all criminal records
export async function getCriminals() {
  const response = await fetch(`${API_BASE_URL}/criminals`);

  if (!response.ok) {
    throw new Error("Failed to fetch criminals");
  }

  const data = await response.json();
  return data.criminals;
}

// Add a new criminal record
export async function createCriminal(criminal) {
  const response = await fetch(`${API_BASE_URL}/criminals`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(criminal),
  });

  if (!response.ok) {
    throw new Error("Failed to create criminal record");
  }

  return await response.json();
}


export async function linkCriminalToCase(link) {
  const response = await fetch(`${API_BASE_URL}/criminal-cases`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(link),
  });

  const data = await response.json();

  if (!response.ok) {
    throw new Error(data.detail || "Failed to link criminal to case");
  }

  return data;
}

export async function deleteCriminalCaseLink(criminalId, caseId) {
  const response = await fetch(`${API_BASE_URL}/criminal-cases/${criminalId}/${caseId}`, {
    method: "DELETE",
  });

  const data = await response.json();

  if (!response.ok) {
    throw new Error(data.detail || "Failed to unlink criminal from case");
  }

  return data;
}
