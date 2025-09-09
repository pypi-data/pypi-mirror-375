class Utilityman < Formula
  include Language::Python::Virtualenv

  desc "Follow any MLB game in your shell - live play-by-play terminal experience"
  homepage "https://github.com/stiles/utilityman"
  url "https://github.com/stiles/utilityman/archive/refs/tags/v0.3.0.tar.gz"
  sha256 "NEEDS_ACTUAL_SHA256_FROM_GITHUB_RELEASE"
  license "MIT"

  depends_on "python@3.11"

  resource "requests" do
    url "https://files.pythonhosted.org/packages/source/r/requests/requests-2.31.0.tar.gz"
    sha256 "942c5a758f98d790eaed1a29cb6eefc7ffb0d1cf7af05c3d2791656dbd6ad1e1"
  end

  def install
    virtualenv_install_with_resources
  end

  test do
    # Test that the binary exists and can show help
    assert_match "Stream MLB play-by-play", shell_output("#{bin}/utilityman --help")
  end
end
