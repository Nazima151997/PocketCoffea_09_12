import ROOT
import numpy as np

# Open ROOT file
file = ROOT.TFile("vhbb_shapes__2L.root")

# Paths
dirpath = "_baseline_mm"
h0_path = f"{dirpath}/ZH_Hto2B_Zto2L_SMEFT_0j_nominal"
h1_path = f"{dirpath}/ZH_Hto2B_Zto2L_SMEFT_1j_nominal"

# Grab histograms
hist_0j = file.Get(h0_path)
hist_1j = file.Get(h1_path)

# Basic checks
if not all(isinstance(h, ROOT.TH1) for h in [hist_0j, hist_1j]):
    print("Error: Histogram(s) not found or not TH1")
    print(f"SMEFT 0j: {type(hist_0j)}  from {h0_path}")
    print(f"SMEFT 1j: {type(hist_1j)}  from {h1_path}")
    raise SystemExit(1)

# Optional: compare shapes only (area-normalize)
normalize_shapes = False
if normalize_shapes:
    if hist_0j.Integral() != 0:
        hist_0j.Scale(1.0 / hist_0j.Integral())
    if hist_1j.Integral() != 0:
        hist_1j.Scale(1.0 / hist_1j.Integral())

# Rebin (use unique names to avoid clashes)
nnn = 5
hist_0j = hist_0j.Rebin(nnn, "h0j_reb")
hist_1j = hist_1j.Rebin(nnn, "h1j_reb")

# Binning
num_bins = hist_1j.GetNbinsX()
bin_centers = np.array([hist_1j.GetBinCenter(i) for i in range(1, num_bins + 1)])

# Style off
ROOT.gStyle.SetOptStat(0)
for h in (hist_0j, hist_1j):
    h.SetTitle("")

# Canvas & pads
canvas = ROOT.TCanvas("canvas", "SMEFT 0j vs 1j", 1200, 1200)
canvas.SetTopMargin(0.08)
canvas.SetBottomMargin(0.02)

pad1 = ROOT.TPad("pad1", "pad1", 0, 0.35, 1, 1)
pad1.SetBottomMargin(0.02)
pad1.SetTopMargin(0.15)
pad1.Draw()
pad1.cd()

# Draw histograms (1j as reference first)
max_val = max(hist_0j.GetMaximum(), hist_1j.GetMaximum())

hist_1j.SetLineColor(ROOT.kGreen + 2)
hist_1j.SetLineWidth(3)
hist_1j.SetMaximum(max_val * 1.5)
hist_1j.GetYaxis().SetTitle("Events / 10 GeV")
hist_1j.GetYaxis().SetTitleOffset(0.9)
hist_1j.GetXaxis().SetLabelSize(0)
hist_1j.GetXaxis().SetTitleSize(0)
hist_1j.Draw("HIST")

hist_0j.SetLineColor(ROOT.kBlue)
hist_0j.SetLineWidth(3)
hist_0j.Draw("HIST SAME")

# Main title
title = ROOT.TLatex()
title.SetNDC(); title.SetTextSize(0.045); title.SetTextFont(42); title.SetTextAlign(21)
title.DrawLatex(0.5, 0.95, "#it{ZH} #rightarrow #it{ll bb} (SMEFT 0j vs 1j)")

# CMS-ish labels (optional)
cms = ROOT.TLatex(); cms.SetNDC(); cms.SetTextSize(0.045); cms.SetTextFont(61)
cms.DrawLatex(0.12, 0.856, "CMS")
prog = ROOT.TLatex(); prog.SetNDC(); prog.SetTextSize(0.035); prog.SetTextFont(52)
prog.DrawLatex(0.19, 0.856, "Progress")
lumi = ROOT.TLatex(); lumi.SetNDC(); lumi.SetTextSize(0.035); lumi.SetTextAlign(31)
lumi.DrawLatex(0.9, 0.856, "59.7 fb^{-1} (13 TeV)")
info = ROOT.TLatex(); info.SetNDC(); info.SetTextSize(0.038)
info.DrawLatex(0.65, 0.5, "Year: 2018")
info.DrawLatex(0.6, 0.45, "Cat: mumu channel, baseline selection")

# Legend
leg = ROOT.TLegend(0.62, 0.65, 0.90, 0.85)
leg.SetTextSize(0.035); leg.SetBorderSize(1); leg.SetFillStyle(1001); leg.SetFillColor(ROOT.kWhite)
leg.addEntry = leg.AddEntry
leg.addEntry(hist_0j, "SMEFT 0j", "l")
leg.addEntry(hist_1j, "SMEFT 1j", "l")
leg.Draw()

# Ratio pad
canvas.cd()
pad2 = ROOT.TPad("pad2", "pad2", 0, 0, 1, 0.35)
pad2.SetTopMargin(0.05)
pad2.SetBottomMargin(0.35)
pad2.Draw()
pad2.cd()

# Ratios: (0j / 1j)
counts_0j = np.array([hist_0j.GetBinContent(i) for i in range(1, num_bins + 1)])
counts_1j = np.array([hist_1j.GetBinContent(i) for i in range(1, num_bins + 1)])
ratios = np.where(counts_1j > 0, counts_0j / counts_1j, 1.0)

graph_ratio = ROOT.TGraph(num_bins, bin_centers, ratios)
graph_ratio.SetMarkerColor(ROOT.kBlue)
graph_ratio.SetMarkerStyle(21)
graph_ratio.SetMarkerSize(1.2)
graph_ratio.SetTitle("")
graph_ratio.GetXaxis().SetTitle("p_{T}^{ll} [GeV]")
graph_ratio.GetYaxis().SetTitle("Ratio (0j / 1j)")
graph_ratio.GetYaxis().SetRangeUser(0, 2)
graph_ratio.GetXaxis().SetRangeUser(0, 400)
graph_ratio.GetXaxis().SetTitleSize(0.08)
graph_ratio.GetYaxis().SetTitleSize(0.08)
graph_ratio.GetXaxis().SetLabelSize(0.07)
graph_ratio.GetYaxis().SetLabelSize(0.07)
graph_ratio.GetYaxis().SetTitleOffset(0.4)
graph_ratio.GetXaxis().SetTitleOffset(1.1)
graph_ratio.Draw("AP")

# Reference line at 1
first_bin_low  = hist_1j.GetBinLowEdge(1)
last_bin_high  = hist_1j.GetBinLowEdge(num_bins) + hist_1j.GetBinWidth(num_bins)
line = ROOT.TLine(first_bin_low, 1, last_bin_high, 1)
line.SetLineColor(ROOT.kBlack); line.SetLineStyle(2); line.SetLineWidth(2)
line.Draw("SAME")

# Save
canvas.SaveAs("ZH_SMEFT0j_vs_1j_dileppt.png")
