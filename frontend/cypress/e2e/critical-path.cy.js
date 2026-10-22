const PASSWORD = "AcmeDemo123!"


function login(email) {
  cy.visit("/login")

  cy.get("input[type=email]")
    .should("be.visible")
    .clear()
    .type(email)

  cy.get("input[type=password]")
    .should("be.visible")
    .clear()
    .type(PASSWORD, { log: false })

  cy.get("button[type=submit]")
    .should("be.enabled")
    .click()

  cy.contains("ACME Workplace", {
    timeout: 10000,
  }).should("be.visible")
}


function logout() {
  cy.contains(
    "button",
    /^Logout$/,
  )
    .should("be.visible")
    .click()

  cy.location("pathname", {
    timeout: 10000,
  }).should("eq", "/login")
}


function openIncidents() {
  cy.contains(
    /^Incidents$/,
  )
    .first()
    .should("be.visible")
    .click()

  cy.location("pathname", {
    timeout: 10000,
  }).should("eq", "/incidents")
}


function typeField(testId, value) {
  cy.get(`[data-cy="${testId}"]`)
    .find("input, textarea")
    .filter(":visible")
    .first()
    .should("be.visible")
    .clear()
    .type(value)
}


function selectField(testId, option) {
  cy.get(
    `[data-cy="${testId}"] [role=combobox]`,
    {
      timeout: 10000,
    },
  )
    .should("be.visible")
    .should(
      "not.have.attr",
      "aria-disabled",
      "true",
    )
    .click()

  cy.get("[role=option]:visible", {
    timeout: 10000,
  })
    .contains(option)
    .should("be.visible")
    .click()
}


function openIncident(title) {
  cy.contains(
    title,
    {
      timeout: 10000,
    },
  )
    .should("be.visible")
    .click()

  cy.contains(
    title,
    {
      timeout: 10000,
    },
  ).should("be.visible")
}


describe("ACME complete critical workflow", () => {
  it("employee reports, admin assigns, engineer resolves, employee closes", () => {
    const title =
      `Cypress Workflow ${Date.now()}`


    // =========================================
    // EMPLOYEE
    // =========================================

    login("employee@acme.inc")

    openIncidents()

    cy.contains(
      "button",
      "Report Incident",
      { timeout: 10000 },
    )
      .filter(":visible")
      .first()
      .scrollIntoView()
      .should("be.enabled")
      .click({ force: true })

    cy.get("[role=dialog]", {
      timeout: 10000,
    })
      .should("be.visible")
      .within(() => {
        cy.contains(
          "Report Workplace Incident",
        ).should("be.visible")
      })


    typeField(
      "incident-title",
      title,
    )

    typeField(
      "incident-description",
      "Full Cypress workflow incident",
    )

    typeField(
      "incident-category",
      "Equipment",
    )


    // Priority
    selectField(
      "incident-priority",
      "High",
    )


    // Building
    cy.intercept(
      "GET",
      "**/floors?building_id=*",
    ).as("floors")

    selectField(
      "incident-building",
      "Tampa Operations Center",
    )

    cy.wait("@floors")
      .its("response.statusCode")
      .should("eq", 200)


    // Floor
    cy.intercept(
      "GET",
      "**/seats?floor_id=*",
    ).as("seats")

    selectField(
      "incident-floor",
      "Floor 1",
    )

    cy.wait("@seats")
      .its("response.statusCode")
      .should("eq", 200)


    // Seat
    selectField(
      "incident-seat",
      "A-101",
    )


    // Submit
    cy.intercept(
      "POST",
      "**/incidents",
    ).as("createIncident")

    cy.get("[role=dialog]")
      .should("be.visible")
      .within(() => {
        cy.contains(
          "button",
          "Report Incident",
        )
          .should("be.visible")
          .should("be.enabled")
          .click()
      })

    cy.wait("@createIncident")
      .its("response.statusCode")
      .should("be.oneOf", [200, 201])


    // Open newly created incident
    openIncident(title)


    // =========================================
    // ADMIN
    // =========================================

    logout()

    login("admin@acme.inc")

    openIncidents()

    openIncident(title)


    selectField(
      "assignment-engineer",
      "Alex Engineer",
    )

    cy.intercept(
      "PUT",
      "**/incidents/*/assignment",
    ).as("assign")

    cy.contains(
      "button",
      /^Assign Engineer$/,
    )
      .should("be.enabled")
      .click()

    cy.wait("@assign")
      .its("response.statusCode")
      .should("eq", 200)

    cy.contains(
      "Engineer assigned.",
      {
        timeout: 10000,
      },
    ).should("be.visible")


    // =========================================
    // ENGINEER
    // =========================================

    logout()

    login("engineer@acme.inc")

    openIncidents()

    openIncident(title)


    // OPEN -> IN PROGRESS
    selectField(
      "incident-status",
      "IN PROGRESS",
    )

    cy.intercept(
      "PUT",
      "**/incidents/*/status",
    ).as("inProgress")

    cy.contains(
      "button",
      /^Update Status$/,
    )
      .should("be.enabled")
      .click()

    cy.wait("@inProgress")
      .its("response.statusCode")
      .should("eq", 200)

    cy.contains(
      "IN_PROGRESS",
      {
        timeout: 10000,
      },
    ).should("be.visible")


    // IN PROGRESS -> RESOLVED
    selectField(
      "incident-status",
      "RESOLVED",
    )

    cy.intercept(
      "PUT",
      "**/incidents/*/status",
    ).as("resolve")

    cy.contains(
      "button",
      /^Update Status$/,
    )
      .should("be.enabled")
      .click()

    cy.wait("@resolve")
      .its("response.statusCode")
      .should("eq", 200)

    cy.contains(
      "RESOLVED",
      {
        timeout: 10000,
      },
    ).should("be.visible")


    // =========================================
    // EMPLOYEE CLOSES IT
    // =========================================

    logout()

    login("employee@acme.inc")

    openIncidents()

    openIncident(title)


    cy.intercept(
      "PUT",
      "**/incidents/*/status",
    ).as("close")

    cy.contains(
      "button",
      /^Close Incident$/,
      {
        timeout: 10000,
      },
    )
      .should("be.visible")
      .click()

    cy.wait("@close")
      .its("response.statusCode")
      .should("eq", 200)

    cy.contains(
      "CLOSED",
      {
        timeout: 10000,
      },
    ).should("be.visible")
  })
})
