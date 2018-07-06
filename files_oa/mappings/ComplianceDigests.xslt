<?xml version="1.0" encoding="UTF-8"?>
<xsl:stylesheet version="2.0"
  xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
  xmlns:t="http://schemas.datacontract.org/2004/07/One.Access.Data"
  xmlns:ms="urn:schemas-microsoft-com:xslt"
  xmlns:dt="urn:schemas-microsoft-com:datatypes">
	<xsl:param name="host"/>
	<xsl:param name="title"/>
	<xsl:template match="t:ComplianceReport">
		<html xmlns="http://www.w3.org/1999/xhtml">
			<head>
				<meta http-equiv="Content-Type" content="text/html; charset=utf-8" />
				<title>
					<xsl:value-of select="$title"/>
				</title>
				<link href='http://fonts.googleapis.com/css?family=Roboto:100,300,500,700' rel='stylesheet' type='text/css' />
			</head>
			<body style="background:#FFF; padding: 0; margin: 0; border: 0">
				<table id="root" style="background-color: #FFFFFF; border-spacing: 0; width: 600px;" cellpadding="0" cellspacing="0">
					<tbody>
						<tr>
							<td>
								<table style="background-color: #1AAEEF; padding:0; margin: 0; border-spacing: 0;" cellpadding="0" cellspacing="0">
									<tbody>
										<tr>
											<td style="width: 800px; height: 60px; line-height: 1px; padding: 0; margin: 0; border-spacing: 0;">
												<p style="margin: 0 0 0 20px">
													<img style="width: 120px; height: 27px; line-height: 1px;" alt="" title="" src="{$host}Content/email/signup/logo-cube.png" />
												</p>
											</td>
										</tr>
									</tbody>
								</table>
							</td>
						</tr>
						<tr>
							<td>
								<table style="margin: 0 15px 0 15px; width:760px; padding: 0; border-spacing: 0;" cellpadding="0" cellspacing="0">
									<tbody>
										<tr>
											<td style="padding: 10px 100px 0 10px;">
												<p style="font: normal normal 500 14px/16px 'Roboto', 'Arial', sans-serif; color: #484949;  margin: 0; padding: 0; text-align: left;" class="name">
													<xsl:value-of select="t:AddresseeName"/>,
												</p>
											</td>
										</tr>
										<tr>
											<td style="padding: 20px 10px 0 10px;">
												<p style="font: normal normal 500 14px/16px 'Roboto', 'Arial', sans-serif; color: #484949;  margin: 0; padding: 0; text-align: left;">
													Below is an attestation report, updated as of <xsl:value-of select="ms:format-date(t:ReportEmailDate, 'MM/dd/yyyy')"/>.
												</p>
											</td>
										</tr>
										<tr>
											<td style="padding: 30px 15px 15px 15px; border: 1px solid #e1e1e1; margin-top: 10px;">
												<p style="margin: 0; text-align: bottom;">
													<span style="font: normal normal 400 16px/16px 'Roboto', 'Arial', sans-serif; color: #1AAEEF;">Compliance Digest Report</span>
													<span style="font: normal normal 400 16px/16px 'Roboto', 'Arial', sans-serif; color: #1AAEEF; float: right;">
														<xsl:value-of select="ms:format-date(t:ReportEmailDate, 'MM/dd/yyyy')"/>
													</span>
												</p>
												<p style="margin: 20px 0 20px 0; text-align: bottom;">
													<span style="font: normal normal 400 16px/16px 'Roboto', 'Arial', sans-serif; color: #000000; padding: 5px 5px 5px 5px; margin: 0;">Outstanding</span>
													<span style="font: normal normal 400 16px/16px 'Roboto', 'Arial', sans-serif; color: #FF9316; float: right; border: 3px solid #FF9316; padding: 5px 8px 5px 8px; margin: 0">
														<xsl:value-of select="t:OutstandingCount"/>
													</span>
												</p>
												<p style="margin: 30px 0 20px 0; text-align: bottom;">
													<span style="font: normal normal 400 16px/16px 'Roboto', 'Arial', sans-serif; color: #000000; padding: 5px 5px 5px 5px; margin: 0;">Pending</span>
													<span style="font: normal normal 400 16px/16px 'Roboto', 'Arial', sans-serif; color: #40fd59; float: right; border: 3px solid #40fd59; padding: 5px 8px 5px 8px; margin: 0">
														<xsl:value-of select="t:PendingCount"/>
													</span>
												</p>
												<p style="margin: 30px 0 20px 0; text-align: bottom;">
													<span style="font: normal normal 400 16px/16px 'Roboto', 'Arial', sans-serif; color: #000000; padding: 5px 5px 5px 5px; margin: 0;">Cancellation</span>
													<span style="font: normal normal 400 16px/16px 'Roboto', 'Arial', sans-serif; color: #A4A9AE; float: right; border: 3px solid #A4A9AE; padding: 5px 8px 5px 8px; margin: 0">
														<xsl:value-of select="t:CancelledCount"/>
													</span>
												</p>
											</td>
										</tr>
										<tr>
											<td style="padding: 5px 10px 150px 10px; border: 1px solid #e1e1e1;">
												<table>
													<tr>
														<td style="margin: 0; padding: 30px 15px 10px 15px; text-align: left; width: 300px;">
															<span style="font: normal normal 400 16px/16px 'Roboto', 'Arial', sans-serif; color: #ED1C24;">OUTSTANDING ATTESTATIONS</span>
														</td>
													</tr>
													<tr>
														<td style="width: 250px;">
															<span style="font: normal normal 400 16px/16px 'Roboto', 'Arial', sans-serif; color: #A4A9AE; padding-left: 25px;">EVENT NAME</span>
														</td>
														<td style="width: 250px;">
															<span style="font: normal normal 400 16px/16px 'Roboto', 'Arial', sans-serif; color: #A4A9AE; float: right;">INVESTOR</span>
														</td>
														<td style="width: 250px;">
															<span style="font: normal normal 400 16px/16px 'Roboto', 'Arial', sans-serif; color: #A4A9AE; float: right;">DUE DATE</span>
														</td>
													</tr>
													<xsl:for-each select="t:OutstandingAttestations/t:ComplianceReport.OutstandingAttestationInfo">
														<tr>
														<td style="width: 250px;">
															<p style="margin: 0; padding: 5px 15px 15px 20px; text-align: bottom;">
																<span style="font: normal normal 400 16px/16px 'Roboto', 'Arial', sans-serif; color: #A4A9AE; float: left; padding: 10px 10px 5px 10px; margin: 0;">
																	<xsl:value-of select="t:EventName" disable-output-escaping="yes"/>
																</span>
															</p>
														</td>
														<td style="width: 250px;">
															<span style="font: normal normal 400 16px/16px 'Roboto', 'Arial', sans-serif; color: #A4A9AE; float: right; padding: 10px 10px 5px 10px; margin: 0;">
																<xsl:value-of select="t:InvestorName"/>
															</span>
														</td>
														<td style="width: 250px;">
															<span style="font: normal normal 400 16px/16px 'Roboto', 'Arial', sans-serif; color: #FF9316; float: right; border: 1px solid #FF9316; padding: 10px 10px 5px 10px; margin: 0;">
																<xsl:value-of select="ms:format-date(t:DueDate, 'MM/dd/yyyy')"/>
															</span>
														</td>
															</tr>
													</xsl:for-each>
												</table>
											</td>
										</tr>
										<tr>
											<td style="padding: 25px 10px 0 10px;">
												<p style="font: normal normal 500 14px/16px 'Roboto', 'Arial', sans-serif; color: #414141; margin:0 0 20px 0" />
											</td>
										</tr>
										<tr>
											<td style="padding: 7px 118px 5px 0; border-top: 1px solid #e1e1e1;" >
												<p style="font: normal normal 400 12px 'Arial', sans-serif; color: #878685; letter-spacing: 0.25px; margin: 11px 0 0 0">
													&#169; 2017 ONEaccess LLC
												</p>
												<p style="font: normal normal 400 12px 'Arial', sans-serif; color: #878685; letter-spacing: 0.25px; margin: 11px 0 0 0">
													ONEaccess LLC | 1140 Broadway, Suite 5 | New York, NY 10001
												</p>
												<p style="font: normal normal 400 12px 'Arial', sans-serif; color: #878685; letter-spacing: 0.25px; margin: 11px 0 0 0">
													We respect your privacy. Please review our <a style="color:#878685; text-decoration: underline;" href="~/Account/PrivacyPolicy">privacy policy</a> for more information about click activity with ONEaccess and links included in this email.
												</p>
												<p style="font: normal normal 400 12px 'Arial', sans-serif; color: #878685; letter-spacing: 0.25px; margin: 11px 0 0 0">
													This email was sent to
												</p>
												<p style="font: normal normal 400 12px 'Arial', sans-serif; color: #878685; letter-spacing: 0.25px; margin: 11px 0">
													If you are not the intended recipient and feel you have received this email in error, you may unsbscribe or update your email preference from your profile information.
												</p>
											</td>
										</tr>
									</tbody>
								</table>
							</td>
						</tr>
					</tbody>
				</table>
			</body>
		</html>
	</xsl:template>
</xsl:stylesheet>