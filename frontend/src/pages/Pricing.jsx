import BackButton from 'components/BackButton.jsx'
function Pricing() {
  return (
    <div className="min-h-screen bg-white p-8">
      <div className="w-12  mt-10">
        <BackButton />
      </div>
      <div className="max-w-4xl mx-auto">
        <stripe-pricing-table pricing-table-id="prctbl_1QUmoHRqMtGFdNkemiX2ROCu"
                              publishable-key="pk_live_51PgjQkRqMtGFdNkeIsnuQauUAMWx71ORiFO9omh9Ki8qRJ3We67YIEBNv3EiCU7R7xHTCcbPwy5BvP36eetNw6jk00rjUlt1ay">
        </stripe-pricing-table>
      </div>
    </div>
  );
}

export default Pricing;
